# Standard Library
from typing import Any

# Django
from django.urls import path

# Libraries
from apps.django_projects.core import views

urlpatterns: list[Any] = [
    path(
        "home-bet/",
        views.HomeBetView.as_view(),
        name="get-home-bet",
    ),
    path(
        "home-bet/multiplier/",
        views.HomeBetMultiplierView.as_view(),
        name="add-multipliers",
    ),
]
