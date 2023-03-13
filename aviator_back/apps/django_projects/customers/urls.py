# Standard Library
from typing import Any

# Django
from django.urls import path

# Internal
from apps.django_projects.customers import views

urlpatterns: list[Any] = [
    path(
        "balance/",
        views.CustomerBalanceView.as_view(),
        name="customer-balance",
    ),
]
