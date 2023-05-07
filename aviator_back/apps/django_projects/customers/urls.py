# Standard Library
from typing import Any

# Django
from django.urls import path

# Internal
from apps.django_projects.customers import views

urlpatterns: list[Any] = [
    path("me/", views.CustomerDataView.as_view(), name="customer-data"),
    path(
        "balance/",
        views.CustomerBalanceView.as_view(),
        name="customer-balance",
    ),
]
