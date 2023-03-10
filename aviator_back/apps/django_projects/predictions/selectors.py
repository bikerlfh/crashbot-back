# Standard Library
from typing import Optional

# Django
from django.db.models import QuerySet

# Internal
from apps.django_projects.predictions.models import (
    ModelCategoryResult,
    ModelHomeBet,
)


def filter_model_home_bet_by_id(
    *, model_home_bet_id: int
) -> QuerySet[ModelHomeBet]:
    return ModelHomeBet.objects.filter(id=model_home_bet_id)


def filter_model_home_bet_by_home_bet_id(
    *, home_bet_id: int, status: Optional[str] = None
) -> QuerySet[ModelHomeBet]:
    filter_ = dict(home_bet_id=home_bet_id)
    if status is not None:
        filter_.update(status=status)
    return ModelHomeBet.objects.filter(**filter_).prefetch_related(
        "category_results"
    )


def get_bets_average_result(
    *, home_bet_id: int, number_of_models: Optional[int] = 3
) -> list[ModelCategoryResult]:
    averages = (
        ModelCategoryResult.objects.filter(home_bet_id=home_bet_id)
        .selected_related("home_bet")
        .order_by("-average_predictions")
        .distinct("model_home_bet_id")[:number_of_models]
    )
    return averages
