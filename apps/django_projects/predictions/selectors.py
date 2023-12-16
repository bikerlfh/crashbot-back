# Standard Library
from typing import Optional

# Django
from django.db.models import F, QuerySet

# Internal
from apps.django_projects.predictions.constants import (
    NUMBER_OF_MODELS_TO_PREDICT,
    ModelStatus,
)
from apps.django_projects.predictions.models import Bot, ModelHomeBetGame


def filter_model_home_bet_game(**kwargs) -> QuerySet[ModelHomeBetGame]:
    return ModelHomeBetGame.objects.filter(**kwargs).prefetch_related(
        "details"
    )


def filter_models_to_generate_category_result() -> QuerySet[ModelHomeBetGame]:
    return (
        ModelHomeBetGame.objects.filter(
            status=ModelStatus.ACTIVE.value,
            home_bet_game__multipliers__multiplier_dt__gt=F("result_date"),
        )
        .order_by("id")
        .distinct("id")
    )


def filter_model_home_bet_by_id(
    *, model_home_bet_game_id: int
) -> QuerySet[ModelHomeBetGame]:
    return filter_model_home_bet_game(id=model_home_bet_game_id)


def filter_model_home_bet_game_by_home_bet_game_id(
    *, home_bet_game_id: int, status: Optional[str] = None
) -> QuerySet[ModelHomeBetGame]:
    filter_ = dict(home_bet_game_id=home_bet_game_id)
    if status is not None:
        filter_.update(status=status)
    return filter_model_home_bet_game(**filter_)


def get_bets_models_by_average_predictions(
    *,
    home_bet_game_id: int,
    number_of_models: Optional[int] = None,
    model_home_bet_id: Optional[int] = None
) -> QuerySet[ModelHomeBetGame]:
    number_of_models = number_of_models or NUMBER_OF_MODELS_TO_PREDICT
    filter_ = dict(
        home_bet_game_id=home_bet_game_id, status=ModelStatus.ACTIVE.value
    )
    if model_home_bet_id is not None:
        filter_.update(id=model_home_bet_id)
        filter_.pop("status")
    models = (
        ModelHomeBetGame.objects.filter(**filter_)
        .prefetch_related("details")
        .order_by("-average_predictions")[:number_of_models]
    )
    return models


def filter_bot(
    bot_id: Optional[int] = None,
    bot_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    **kwargs
) -> QuerySet[Bot]:
    kwargs = dict(**kwargs)
    if bot_id is not None:
        kwargs.update(id=bot_id)
    if bot_type is not None:
        kwargs.update(bot_type=bot_type)
    if is_active is not None:
        kwargs.update(is_active=is_active)
    return Bot.objects.filter(**kwargs).prefetch_related("conditions")
