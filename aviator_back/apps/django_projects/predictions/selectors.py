from typing import Optional
from django.db.models import QuerySet
from apps.django_projects.predictions.models import ModelHomeBet, ModelAverageResult


def filter_model_home_bet_by_id(
    *,
    model_home_bet_id: int
) -> QuerySet[ModelHomeBet]:
    return ModelHomeBet.objects.filter(id=model_home_bet_id)


def get_bets_average_result(
    *,
    home_bet_id: int,
    number_of_models: Optional[int] = 3
) -> list[ModelAverageResult]:
    averages = ModelAverageResult.objects.filter(
        home_bet_id=home_bet_id
    ).selected_related(
        "home_bet"
    ).order_by(
        '-average_predictions'
    ).distinct('model_home_bet_id')[:number_of_models]
    return averages

