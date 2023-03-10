# Standard Library
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

# Django
from rest_framework.exceptions import ValidationError

# Internal
from apps.django_projects.core import selectors as core_selectors
from apps.django_projects.predictions import selectors
from apps.django_projects.predictions.models import (
    ModelCategoryResult,
    ModelHomeBet,
)
from apps.prediction import services as prediction_services
from apps.prediction.constants import ModelType


def create_model_home_bet(
    *,
    home_bet_id: int,
    name: str,
    model_type: ModelType,
    length_window: int,
    others: Optional[dict] = {},
) -> ModelHomeBet:
    home_bet_exists = core_selectors.filter_home_bet(
        home_bet_id=home_bet_id
    ).exists()
    if not home_bet_exists:
        raise ValidationError(
            f"create_model_home_bet :: "
            f"home bet {home_bet_id} does not exists"
        )
    model = ModelHomeBet.objects.create(
        home_bet_id=home_bet_id,
        name=name,
        model_type=model_type.value,
        length_window=length_window,
        others=others,
    )
    return model


def create_model_average_result(
    *,
    model_home_bet_id: int,
    category: int,
    result_date: date,
    correct_predictions: int,
    incorrect_predictions: int,
    percentage_predictions: Decimal,
    correct_bets: int,
    incorrect_bets: int,
    percentage_bets: Decimal,
    other_info: Optional[dict] = {},
) -> ModelCategoryResult:
    model = selectors.filter_model_home_bet_by_id(
        model_home_bet_id=model_home_bet_id
    ).first()
    if not model:
        raise ValidationError(
            f"create_model_average_result :: "
            f"model home bet {model_home_bet_id} does not exists"
        )
    average = ModelCategoryResult.objects.create(
        model_home_bet_id=model_home_bet_id,
        category=category,
        result_date=result_date,
        correct_predictions=correct_predictions,
        incorrect_predictions=incorrect_predictions,
        percentage_predictions=round(percentage_predictions, 2),
        correct_bets=correct_bets,
        incorrect_bets=incorrect_bets,
        percentage_bets=round(percentage_bets, 2),
        other_info=other_info,
    )
    return average


def generate_average_result_of_model(*, model_home_bet_id: int) -> None:
    model_home_bet = selectors.filter_model_home_bet_by_id(
        model_home_bet_id=model_home_bet_id
    ).first()
    if not model_home_bet:
        raise ValidationError(
            f"generate_average_result_of_model :: "
            f"model home bet {model_home_bet_id} does not exists"
        )
    multipliers = core_selectors.get_last_multipliers(
        home_bet_id=model_home_bet.home_bet_id
    )
    average_result = prediction_services.evaluate_model_home_bet(
        model_home_bet=model_home_bet, multipliers=multipliers
    )

    # save total averages
    model_home_bet.average_predictions = average_result.average_predictions
    model_home_bet.average_bets = average_result.average_bets
    model_home_bet.save()
    now = datetime.now().date()
    for key, value in average_result.categories_data.items():
        category_ = model_home_bet.averages.filter(category=key).first()
        if category_:
            category_.result_date = now
            category_.correct_predictions = value.correct_predictions
            category_.incorrect_predictions = value.incorrect_predictions
            category_.percentage_predictions = value.percentage_predictions
            category_.correct_bets = value.correct_bets
            category_.incorrect_bets = value.incorrect_bets
            category_.percentage_bets = value.percentage_bets
            category_.other_info = value.other_info
            category_.save()
            continue
        # create a new category_averages
        create_model_average_result(
            model_home_bet_id=model_home_bet_id,
            category=key,
            result_date=now,
            correct_predictions=value.correct_predictions,
            incorrect_predictions=value.incorrect_predictions,
            percentage_predictions=value.percentage_predictions,
            correct_bets=value.correct_bets,
            incorrect_bets=value.incorrect_bets,
            percentage_bets=value.percentage_bets,
            other_info=value.other_info,
        )


def predict(
    *,
    home_bet_id: int,
    multipliers: Optional[list[Decimal]] = None,
) -> dict:
    home_bet_exists = core_selectors.filter_home_bet(
        home_bet_id=home_bet_id
    ).exists()
    if not home_bet_exists:
        raise ValidationError(
            f"predict :: " f"home bet {home_bet_id} does not exists"
        )
    if not multipliers:
        multipliers = core_selectors.get_last_multipliers(
            home_bet_id=home_bet_id, count=100
        )
    average_models = selectors.get_bets_average_result(home_bet_id=home_bet_id)
    if not average_models:
        raise ValidationError("predict :: no models")
    predictions = []
    for average_model in average_models:
        model_home_bet = average_model.model_home_bet
        prediction_value = prediction_services.predict(
            model_home_bet=model_home_bet, multipliers=multipliers
        )
        predictions.append(
            dict(
                model=model_home_bet.name,
                average_predictions=average_model.average_predictions,
                prediction_value=prediction_value,
            )
        )
    data = dict(predictions=predictions)
    return data
