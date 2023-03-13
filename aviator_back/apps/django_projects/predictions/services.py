# Standard Library
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

# Django
from rest_framework.exceptions import ValidationError

# Internal
from apps.django_projects.core import selectors as core_selectors
from apps.django_projects.predictions import selectors
from apps.django_projects.predictions.constants import (
    DEFAULT_SEQ_LEN,
    PERCENTAGE_ACCEPTABLE,
    PERCENTAGE_MODEL_TO_INACTIVE,
    ModelStatus,
)
from apps.django_projects.predictions.models import (
    ModelCategoryResult,
    ModelHomeBet,
)
from apps.prediction import services as prediction_services
from apps.prediction.constants import ModelType

logger = logging.getLogger(__name__)


def create_model_home_bet(
    *,
    home_bet_id: int,
    name: str,
    model_type: ModelType,
    seq_len: int,
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
        seq_len=seq_len,
        others=others,
    )
    return model


def create_model_average_result(
    *,
    model_home_bet_id: int,
    category: int,
    correct_predictions: int,
    incorrect_predictions: int,
    percentage_predictions: float,
    correct_bets: int,
    incorrect_bets: int,
    percentage_bets: float,
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
        correct_predictions=correct_predictions,
        incorrect_predictions=incorrect_predictions,
        percentage_predictions=round(percentage_predictions, 2),
        correct_bets=correct_bets,
        incorrect_bets=incorrect_bets,
        percentage_bets=round(percentage_bets, 2),
        other_info=other_info,
    )
    return average


def generate_category_result_of_model(*, model_home_bet_id: int) -> None:
    print("---------------------------------------------------------")
    print(f"generation category result for model {model_home_bet_id}")
    print("---------------------------------------------------------")
    model_home_bet = selectors.filter_model_home_bet_by_id(
        model_home_bet_id=model_home_bet_id
    ).first()
    if not model_home_bet:
        raise ValidationError(
            f"generate_average_result_of_model :: "
            f"model home bet {model_home_bet_id} does not exists"
        )
    now = datetime.now()
    multipliers = core_selectors.get_last_multipliers(
        home_bet_id=model_home_bet.home_bet_id,
        count=200
    )
    average_result = prediction_services.evaluate_model_home_bet(
        model_home_bet=model_home_bet, multipliers=multipliers
    )
    # save total averages
    model_home_bet.result_date = now
    model_home_bet.average_predictions = average_result.average_predictions
    model_home_bet.average_bets = average_result.average_bets
    model_home_bet.save()
    for key, value in average_result.categories_data.items():
        category_ = model_home_bet.category_results.filter(
            category=key
        ).first()
        if category_:
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
    models = selectors.get_bets_models_by_average_predictions(
        home_bet_id=home_bet_id
    )
    if not models:
        raise ValidationError("predict :: no models")
    predictions = []
    for model_home_bet in models:
        prediction_value = prediction_services.predict(
            model_home_bet=model_home_bet, multipliers=multipliers
        )
        prediction_round = round(prediction_value, 0)
        if prediction_round < 1:
            prediction_round = 1
        elif prediction_round > 3:
            prediction_round = 3
        category_data = model_home_bet.category_results.filter(
            category=prediction_round
        ).values('percentage_predictions').first()
        percentage_predictions = category_data["percentage_predictions"]
        predictions.append(
            dict(
                id=model_home_bet.id,
                model=model_home_bet.name,
                prediction=prediction_value,
                prediction_round=prediction_round,
                average_predictions=model_home_bet.average_predictions,
                category_percentage=percentage_predictions
            )
        )
    data = dict(predictions=predictions)
    return data


def create_model_with_all_multipliers(
    *,
    home_bet_id: int,
    seq_len: int,
    model_type: Optional[ModelType] = ModelType.SEQUENTIAL,
) -> ModelHomeBet | None:
    home_bet_exists = core_selectors.filter_home_bet(
        home_bet_id=home_bet_id
    ).exists()
    if not home_bet_exists:
        logger.error(
            f"create_model_with_all_multipliers :: "
            f"home bet {home_bet_id} does not exists"
        )
        return
    multipliers = core_selectors.get_last_multipliers(
        home_bet_id=home_bet_id
    )
    if not multipliers:
        logger.warning(
            f"create_model_with_all_multipliers :: "
            f"no multipliers for home bet {home_bet_id}"
        )
        return
    match model_type:
        case ModelType.SEQUENTIAL:
            name, eval_error = prediction_services.create_sequential_model(
                home_bet_id=home_bet_id,
                multipliers=multipliers,
                seq_len=seq_len,
            )
        case ModelType.SEQUENTIAL_LSTM:
            name, eval_error = (
                prediction_services.create_sequential_lstm_model(
                    home_bet_id=home_bet_id,
                    multipliers=multipliers,
                    seq_len=seq_len,
                )
            )
        case _:
            logger.error(
                f"create_model_with_all_multipliers :: "
                f"model type {model_type.value} not implemented"
            )
            return
    model_home_bet = create_model_home_bet(
        home_bet_id=home_bet_id,
        name=name,
        model_type=model_type,
        seq_len=seq_len,
        others=dict(
            eval_error=eval_error,
            num_multipliers_to_train=len(multipliers)
        ),
    )
    generate_category_result_of_model(model_home_bet_id=model_home_bet.id)
    return model_home_bet


def create_model_for_all_in_play_home_bet() -> None:
    """
    create model for all in-play home bets
    (multipliers created no more than 10 minutes ago)
    """
    now = datetime.now()
    home_bet_ids = core_selectors.filter_home_bet(
        filter_=dict(
            multipliers__multiplier_dt__gte=now
        )
    ).values_list('id', flat=True)
    for home_bet_id in home_bet_ids:
        best_model = selectors.get_bets_models_by_average_predictions(
            home_bet_id=home_bet_id,
            number_of_models=1
        ).first()

        if best_model and \
                best_model.average_predictions >= PERCENTAGE_ACCEPTABLE:
            continue
        create_model_with_all_multipliers(
            home_bet_id=home_bet_id,
            seq_len=DEFAULT_SEQ_LEN,
            model_type=ModelType.SEQUENTIAL_LSTM
        )
        # create_model_with_all_multipliers(
        #     home_bet_id=home_bet_id,
        #     seq_len=DEFAULT_SEQ_LEN,
        #     model_type=ModelType.SEQUENTIAL
        # )


def generate_category_results_of_models():
    models = selectors.filter_model_home_bet(
        status=ModelStatus.ACTIVE.value
    ).order_by('id')
    for model in models:
        generate_category_result_of_model(model_home_bet_id=model.id)
        model.refresh_from_db()
        if model.average_predictions < PERCENTAGE_MODEL_TO_INACTIVE:
            model.status = ModelStatus.INACTIVE.value
            model.save()


def get_models_home_bet(
    *, home_bet_id: int, status: Optional[str] = ModelStatus.ACTIVE.value
) -> list[dict]:
    home_bet_exists = core_selectors.filter_home_bet(
        home_bet_id=home_bet_id
    ).exists()
    if not home_bet_exists:
        raise ValidationError(f"home bet {home_bet_id} does not exists")
    models = selectors.filter_model_home_bet_by_home_bet_id(
        home_bet_id=home_bet_id, status=status
    ).order_by("-average_predictions")
    data = []
    for model in models:
        categories = []
        for category in model.category_results.order_by("category"):
            categories.append(
                dict(
                    category=category.category,
                    correct_predictions=category.correct_predictions,
                    incorrect_predictions=category.incorrect_predictions,
                    percentage_predictions=category.percentage_predictions,
                    correct_bets=category.correct_bets,
                    incorrect_bets=category.incorrect_bets,
                    percentage_bets=category.percentage_bets,
                    other_info=category.other_info,
                )
            )
        data.append(
            dict(
                id=model.id,
                name=model.name,
                home_bet_id=model.home_bet_id,
                model_type=model.model_type,
                status=model.status,
                seq_len=model.seq_len,
                average_predictions=model.average_predictions,
                average_bets=model.average_bets,
                result_date=model.result_date,
                others=model.others,
                category_results=categories,
            )
        )
    return data
