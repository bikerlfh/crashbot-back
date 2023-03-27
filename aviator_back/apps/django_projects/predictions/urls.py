# Standard Library
from typing import Any

# Django
from django.urls import path

# Internal
from apps.django_projects.predictions import views

urlpatterns: list[Any] = [
    path(
        "predict/",
        views.PredictionView.as_view(),
        name="prediction-view",
    ),
    path(
        "models/",
        views.ModelHomeBetView.as_view(),
        name="model-home-bet-view",
    ),
    path(
        "strategy/",
        views.PlayerStrategyView.as_view(),
        name="player-strategies-view",
    ),
]
