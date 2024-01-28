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
        # Add other fields as necessary

        # Check if diver already exists
        if Diver.objects.filter(name=diver_name).exists():
            return JsonResponse({'message': 'Diver already exists'}, status=400)
        
        new_diver = Diver(name = diver_name)
        new_diver.save()
        return JsonResponse({'message':'Diver added successfully'}, status=200)

        # try:
        #     # Attempt to create a new User and Diver
        #     user = User.objects.create_user(username=username)
        #     Diver.objects.create(user=user)
        #     messages.success(request, "Diver added successfully")
        #     return redirect("add_diver")  # Redirect to another page

        # except IntegrityError:
        #     messages.error(request, "A user with that username already exists.")
    return JsonResponse({'message': 'Invalid request'}, status=400)

    # return render(request, "bingo/add_diver.html")


def get_creatures_from_sheet():
    # Path to your service account key
    service_account_file = "bingo-408514-4bd65e543418.json"

    creds = None
    creds, _ = google.auth.load_credentials_from_file(service_account_file)
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    spreadsheet_id = "1qAM8jLKCEASjyBjVTqXLgt8YjJRm9OtlIzGQ_xuiGeg"  # Extract from your spreadsheet URL
    range_name = "Sheet1!A2:D"  # Adjust the range accordingly
    result = (
        sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    )
    values = result.get("values", [])

    creatures = []
    if values:
        for row in values:
            # Assuming the spreadsheet has Species, Latin Name, Points, Category in this order
            creature = {
                "species": row[0],
                "latin_name": row[1],
                "points": int(row[2]),  # Convert points to integer
                "category": row[3],
            }
            creatures.append(creature)

    return creatures


def add_observation(request):
    divers = Diver.objects.all()

    creatures = get_creatures_from_sheet()

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
        date_observed = request.POST.get(
            "date_observed"
        )  # get date_observed from POST data

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
        if request.is_ajax():
            return JsonResponse({"message": "Observation submitted successfully!"})
        # Add a success message
        messages.success(request, "Observation submitted successfully!")

        # return redirect("add_observation")

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
