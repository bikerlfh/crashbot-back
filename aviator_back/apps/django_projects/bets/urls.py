# Standard Library
from typing import Any

# Django
from django.urls import path

# Internal
from apps.django_projects.bets import views

urlpatterns: list[Any] = [
    path(
        "bet/",
        views.BetView.as_view(),
        name="bets",
    ),
    path(
        "balance/",
        views.CustomerBalanceView.as_view(),
        name="customer-balance",
    ),
]
