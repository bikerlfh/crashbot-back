# Standard Library
from typing import Optional

# Django
from django.db.models import QuerySet

# Internal
from apps.django_projects.predictions.models import (
    ModelCategoryResult,
    ModelHomeBet,
)


def filter_model_home_bet(**kwargs) -> QuerySet[ModelHomeBet]:
    return ModelHomeBet.objects.filter(**kwargs)


def filter_model_home_bet_by_id(
    *, model_home_bet_id: int
) -> QuerySet[ModelHomeBet]:
    return filter_model_home_bet(id=model_home_bet_id)


def filter_model_home_bet_by_home_bet_id(
    *, home_bet_id: int, status: Optional[str] = None
) -> QuerySet[ModelHomeBet]:
    filter_ = dict(home_bet_id=home_bet_id)
    if status is not None:
        filter_.update(status=status)
    return filter_model_home_bet(**filter_).prefetch_related(
        "category_results"
    )


def get_bets_models_by_average_predictions(
    *, home_bet_id: int, number_of_models: Optional[int] = 3
) -> QuerySet[ModelHomeBet]:
    models = filter_model_home_bet_by_home_bet_id(
        home_bet_id=home_bet_id
    ).order_by(
        "-average_predictions"
    )[:number_of_models]
    return models
