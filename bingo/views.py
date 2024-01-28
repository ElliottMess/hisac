from datetime import datetime, timedelta

import google.auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from .models import Creature, Diver, Observation


def one_page(request):
    last_30_observations = Observation.objects.all().order_by("-date_observed")[:30]
    creatures = Creature.objects.all()  # Assuming Creature is your model
    divers = Diver.objects.all()  # Assuming Diver is your model

    context = {
        "observations": last_30_observations,
        "creatures": creatures,
        "divers": divers,
    }

    return render(request, "bingo/one_page.html", context)


def top_divers_view(request):
    time_period = request.GET.get("period", "month")  # Default to 'month'
    # Logic to get top_divers data based on the time period
    if time_period == "week":
        start_date = datetime.now() - timedelta(days=7)
    elif time_period == "last_six_months":
        start_date = datetime.now() - timedelta(days=180)
    elif time_period == "ever":
        start_date = datetime.now() - timedelta(days=180000)
    else:  # default is month
        start_date = datetime.now() - timedelta(days=30)

    if request.is_ajax():
        html = render_to_string(
            "bingo/top_divers.html",
            {"top_divers": top_divers, "time_period": time_period},
            request,
        )
        return HttpResponse(html)


def top_divers(request):
    time_period = request.GET.get("period", "month")

    # Set the start date based on the selected time period
    if time_period == "week":
        start_date = datetime.now() - timedelta(days=7)
    elif time_period == "last_six_months":
        start_date = datetime.now() - timedelta(days=180)
    elif time_period == "ever":
        start_date = datetime.now() - timedelta(days=180000)
    else:  # default is month
        start_date = datetime.now() - timedelta(days=30)

    # Query to calculate the top 10 divers based on observations since start_date
    top_divers = (
        Observation.objects.filter(date_observed__gte=start_date)
        .values("diver__name")
        .annotate(total_points=Sum("creature__points"))
        .order_by("-total_points")[:10]
    )

    context = {"top_divers": top_divers, "time_period": time_period}

    return render(request, "bingo/top_divers.html", context)


def add_diver(request):
    if request.method == "POST":
        diver_name = request.POST.get("diver_name")

        # Validate the input
        if not diver_name:
            return JsonResponse({"message": "Diver name is required"}, status=400)

        if Diver.objects.filter(name=diver_name).exists():
            return JsonResponse({"message": "Diver already exists"}, status=400)

        try:
            # Create a new Diver instance
            diver = Diver(name=diver_name)
            diver.save()

            # Return a success response
            return JsonResponse({"message": "Diver added successfully"}, status=200)

        except Exception as e:
            # Handle any exceptions that occur
            return JsonResponse({"message": str(e)}, status=500)

    # If not a POST request, you might redirect or show an error
    return JsonResponse({"message": "Invalid request"}, status=400)


def get_creatures_from_sheet():
    service_account_file = "hisac/bingo-408514-4bd65e543418.json"

    # Define the scope and create credentials
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(service_account_file, scopes=scopes)

    # Build the service
    service = build("sheets", "v4", credentials=creds)

    # Specify your Google Sheet ID and the range to read
    spreadsheet_id = "1qAM8jLKCEASjyBjVTqXLgt8YjJRm9OtlIzGQ_xuiGeg"
    range_name = "Sheet1!A2:D"  # Adjust as per your sheet's structure

    # Make the API request
    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    )
    values = result.get("values", [])

    # Define your column headers here (adjust as per your sheet's actual headers)
    headers = ["species", "latin_name", "points", "category"]

    if not values:
        print("No data found.")
        return []
    else:
        # Convert each row into a dictionary
        creatures = []
        for row in values:
            # Create a dictionary for each row, zip with headers
            creature = dict(zip(headers, row))
            creatures.append(creature)

        return creatures


def add_observation(request):
    divers = Diver.objects.all()

    creatures = get_creatures_from_sheet()
    print(creatures)

    # Add or update creatures in the Creature table
    for creature in creatures:
        try:
            existing_creature = Creature.objects.get(species=creature["species"])
            if (
                existing_creature.latin_name != creature["latin_name"]
                or existing_creature.points != creature["points"]
                or existing_creature.category != creature["category"]
            ):
                existing_creature.latin_name = creature["latin_name"]
                existing_creature.points = creature["points"]
                existing_creature.category = creature["category"]
                existing_creature.save()
        except Creature.DoesNotExist:
            Creature.objects.create(
                species=creature["species"],
                latin_name=creature["latin_name"],
                points=creature["points"],
                category=creature["category"],
            )

    if request.method == "POST":
        diver_id = request.POST.get("diver")
        creature_id = request.POST.get("creature")
        try:
            date_observed = datetime.strptime(
                request.POST.get("date_observed"), "%Y-%m-%d"
            ).date()
            if date_observed > datetime.now().date():
                return JsonResponse(
                    {"message": "The observation date cannot be in the future."},
                    status=400,
                )

        except ValueError:
            return JsonResponse(
                {"message": "Invalid date format. Please use YYYY-MM-DD."},
                status=400,
            )

        # Validate the input
        if not diver_id or not creature_id or not date_observed:
            return HttpResponseBadRequest("Invalid input")

        try:
            diver = Diver.objects.get(id=diver_id)
            creature = Creature.objects.get(species=creature_id)
        except (Diver.DoesNotExist, Creature.DoesNotExist):
            return HttpResponseBadRequest("Diver or Creature not found")

        # Create a new observation
        Observation.objects.create(
            diver=diver, creature=creature, date_observed=date_observed
        )

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # This is an AJAX request
            return JsonResponse(
                {"message": "Observation submitted successfully!"}
            )  # Add a success message
        messages.success(request, "Observation submitted successfully!")

        return redirect("add_observation")

    return render(
        request,
        "bingo/add_observation.html",
        {"divers": divers, "creatures": creatures},
    )


def creatures_list(request):
    creatures = Creature.objects.all()
    return render(request, "bingo/creatures_list.html", {"creatures": creatures})


def observations_list(request):
    observations = Observation.objects.all()
    return render(
        request, "bingo/observations_list.html", {"observations": observations}
    )
