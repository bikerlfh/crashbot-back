# Standard Library
from typing import Any

# Django
from django.urls import path

# Internal
from apps.core import views

urlpatterns: list[Any] = [
    path(
        "homebet/multiplier/add/",
        views.AddHomeBetResult.as_view(),
        name="add-multipliers",
    ),
]
