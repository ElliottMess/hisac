"""
URL configuration for hisac project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from bingo import views

urlpatterns = [
    path("", views.one_page, name="home"),
    path("admin/", admin.site.urls),
    path("top_divers/", views.top_divers, name="top_divers"),
    path("add_diver/", views.add_diver, name="add_diver"),
    path("add_observation/", views.add_observation, name="add_observation"),
    path("creatures/", views.creatures_list, name="creatures_list"),
    path("observations/", views.observations_list, name="observations_list"),
    path("observations/", views.observations_list, name="observations_list"),
]
