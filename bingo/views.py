from datetime import datetime, timedelta

import google.auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from .forms import DiverForm
from .models import Booster, Creature, Diver, Observation


def one_page(request):
    sync_boosters_from_sheet()
    sync_creatures_from_sheet()

    last_30_observations = Observation.objects.all().order_by("-date_observed")[:30]
    creatures = Creature.objects.all()  # Assuming Creature is your model
    divers = Diver.objects.all()  # Assuming Diver is your model
    boosters = Booster.objects.all()  # Assuming Booster is your model

    context = {
        "observations": last_30_observations,
        "creatures": creatures,
        "divers": divers,
        "diver_form": DiverForm(),
        "boosters": boosters,
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
        form = DiverForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            if Diver.objects.filter(name__iexact=name).exists():
                # Directly return the specific error message
                return JsonResponse(
                    {"status": "error", "message": "This diver already exists."},
                    status=400,
                )
            form.save()
            return JsonResponse(
                {"status": "success", "message": "Diver added successfully!"}
            )
        else:
            # Generic form error
            return JsonResponse(
                {"status": "error", "message": "Invalid input."}, status=400
            )
    else:
        # Not a POST request
        return JsonResponse(
            {"status": "error", "message": "Invalid request method."}, status=400
        )


# def get_creatures_from_sheet():
#     service_account_file = "hisac/bingo-408514-4bd65e543418.json"

#     # Define the scope and create credentials
#     scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
#     creds = Credentials.from_service_account_file(service_account_file, scopes=scopes)

#     # Build the service
#     service = build("sheets", "v4", credentials=creds)

#     # Specify your Google Sheet ID and the range to read
#     spreadsheet_id = "1qAM8jLKCEASjyBjVTqXLgt8YjJRm9OtlIzGQ_xuiGeg"
#     range_name = "Sheet1!A2:D"  # Adjust as per your sheet's structure

#     # Make the API request
#     sheet = service.spreadsheets()
#     result = (
#         sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
#     )
#     values = result.get("values", [])

#     # Define your column headers here (adjust as per your sheet's actual headers)
#     headers = ["species", "latin_name", "points", "category"]

#     if not values:
#         print("No data found.")
#         return []
#     else:
#         # Convert each row into a dictionary
#         creatures = []
#         for row in values:
#             # Create a dictionary for each row, zip with headers
#             creature = dict(zip(headers, row))
#             creatures.append(creature)

#         return creatures


# def get_booster_from_sheet():
#     service_account_file = "hisac/bingo-408514-4bd65e543418.json"

#     # Define the scope and create credentials
#     scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
#     creds = Credentials.from_service_account_file(service_account_file, scopes=scopes)

#     # Build the service
#     service = build("sheets", "v4", credentials=creds)

#     # Specify your Google Sheet ID and the range to read
#     spreadsheet_id = "1qAM8jLKCEASjyBjVTqXLgt8YjJRm9OtlIzGQ_xuiGeg"
#     range_name = "Sheet1!F2:G"  # Adjust as per your sheet's structure

#     # Make the API request
#     sheet = service.spreadsheets()
#     result = (
#         sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
#     )
#     values = result.get("values", [])

#     # Define your column headers here (adjust as per your sheet's actual headers)
#     headers = ["boosters", "coefficient"]

#     if not values:
#         print("No data found.")
#         return []
#     else:
#         # Convert each row into a dictionary
#         boosters = []
#         for row in values:
#             # Create a dictionary for each row, zip with headers
#             booster = dict(zip(headers, row))
#             boosters.append(booster)

#         return boosters


def sync_boosters_from_sheet():
    service_account_file = "hisac/bingo-408514-4bd65e543418.json"
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(service_account_file, scopes=scopes)
    service = build("sheets", "v4", credentials=creds)

    # The ID and range of your Google Sheet.
    spreadsheet_id = "1qAM8jLKCEASjyBjVTqXLgt8YjJRm9OtlIzGQ_xuiGeg"
    range_name = "Sheet1!F2:G"  # Adjust as per your sheet's structure

    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    )
    values = result.get("values", [])

    if not values:
        print("No data found in sheet.")
        return

    # Assuming your Google Sheet has two columns: Name and Score
    for row in values:
        # Create or update your model instance here
        booster, coefficient = row
        obj, created = Booster.objects.update_or_create(
            booster=booster,
            defaults={"coefficient": coefficient},
        )


def sync_creatures_from_sheet():
    service_account_file = "hisac/bingo-408514-4bd65e543418.json"
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(service_account_file, scopes=scopes)
    service = build("sheets", "v4", credentials=creds)

    # The ID and range of your Google Sheet.
    spreadsheet_id = "1qAM8jLKCEASjyBjVTqXLgt8YjJRm9OtlIzGQ_xuiGeg"
    range_name = "Sheet1!A2:D"  # Adjust as per your sheet's structure

    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    )
    values = result.get("values", [])
    #     headers = ["species", "latin_name", "points", "category"]

    if not values:
        print("No data found in sheet.")
        return

    # Assuming your Google Sheet has two columns: Name and Score
    for row in values:
        # Create or update your model instance here
        species, latin_name, points, category = row
        obj, created = Creature.objects.update_or_create(
            species=species,
            latin_name=latin_name,
            points=points,
            defaults={"category": category},
        )


def add_observation(request):

    sync_boosters_from_sheet()
    sync_creatures_from_sheet()

    divers = Diver.objects.all()

    creatures = Creature.objects.all()

    boosters = Booster.objects.all()

    # Now, fetch and group creatures by categories for the dropdown
    grouped_creatures = Creature.objects.order_by("category", "species")

    # Prepare categories and their creatures for the template
    categories_with_creatures = {}
    for creature in grouped_creatures:
        category_name = creature.category
        if category_name not in categories_with_creatures:
            categories_with_creatures[category_name] = []
        categories_with_creatures[category_name].append(creature)

    if request.method == "POST":
        diver_id = request.POST.get("diver")
        creature_id = request.POST.get("creature")
        booster_ids = request.POST.getlist("booster")
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
            return JsonResponse(
                {"message": "Invalid input"},
                status=400,
            )

        try:
            diver = Diver.objects.get(id=diver_id)
            creature = Creature.objects.get(species=creature_id)
        except (Diver.DoesNotExist, Creature.DoesNotExist):
            return JsonResponse(
                {"message": "Creature or diver does not exist"},
                status=400,
            )

            # Calculate total coefficient based on selected boosters
        total_coefficient = 1.0
        for booster_id in booster_ids:
            booster = get_object_or_404(
                Booster, id=booster_id
            )  # Assuming you have a Booster model or replace with sheet logic
            total_coefficient *= booster.coefficient

        # Create the observation with the calculated points
        points_with_boost = creature.points * total_coefficient

        try:
            # Create a new Diver instance
            observation = Observation(
                diver=diver,
                creature=creature,
                date_observed=date_observed,
                points=points_with_boost,
            )
            observation.save()

            # Return a success response
            return JsonResponse(
                {"message": "Observation added successfully"}, status=200
            )

        except Exception as e:
            # Handle any exceptions that occur
            return JsonResponse({"message": str(e)}, status=500)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # This is an AJAX request
            return JsonResponse(
                {"message": "Observation submitted successfully!"}
            )  # Add a success message
        messages.success(request, "Observation submitted successfully!")

    # If not a POST request, you might redirect or show an error
    return JsonResponse({"message": "Invalid request"}, status=400)


def creatures_list(request):
    creatures = Creature.objects.all()
    return render(request, "bingo/creatures_list.html", {"creatures": creatures})


def observations_list(request):
    observations = Observation.objects.all()
    return render(
        request, "bingo/observations_list.html", {"observations": observations}
    )
