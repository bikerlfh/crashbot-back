# Standard Library
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

# Django
from django.db.models import Max, Q
from rest_framework.exceptions import ValidationError

# Internal
from apps.django_projects.core import selectors as core_selectors
from apps.django_projects.core.models import HomeBet
from apps.django_projects.predictions import selectors
from apps.django_projects.predictions.constants import (
    DEFAULT_SEQ_LEN,
    GENERATE_AUTOMATIC_MODEL_TYPES,
    PERCENTAGE_ACCEPTABLE,
    PERCENTAGE_MODEL_TO_INACTIVE,
    DIFF_MULTIPLIERS_TO_GENERATE_NEW_MODEL,
    NUMBER_OF_MULTIPLIERS_TO_GENERATE_RESULTS,
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
    home_bet: HomeBet,
    name: str,
    model_type: ModelType,
    seq_len: int,
    others: Optional[dict] = {},
) -> ModelHomeBet:
    model = ModelHomeBet.objects.create(
        home_bet=home_bet,
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


def generate_category_result_of_model(*, model_home_bet: ModelHomeBet) -> None:
    model_home_bet_id = model_home_bet.id
    print("---------------------------------------------------------")
    print(f"generation category result for model {model_home_bet_id}")
    print("---------------------------------------------------------")
    now = datetime.now()
    multipliers = core_selectors.get_last_multipliers(
        home_bet_id=model_home_bet.home_bet_id,
        count=NUMBER_OF_MULTIPLIERS_TO_GENERATE_RESULTS
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
    model_home_bet_id: Optional[int] = None,
) -> dict:
    models = selectors.get_bets_models_by_average_predictions(
        home_bet_id=home_bet_id,
        model_home_bet_id=model_home_bet_id,
    )
    if not models:
        raise ValidationError("no models")
    if not multipliers:
        max_ = models.aggregate(max=Max("seq_len"))["max"]
        multipliers = core_selectors.get_last_multipliers(
            home_bet_id=home_bet_id, count=max_
        )
        if not multipliers:
            raise ValidationError("no multipliers")
    predictions = []
    for model_home_bet in models:
        prediction_data = prediction_services.predict(
            model_home_bet=model_home_bet, multipliers=multipliers
        )
        prediction = prediction_data.prediction
        prediction_round = prediction_data.prediction_round
        probability = prediction_data.probability
        category_data = (
            model_home_bet.category_results.filter(category=prediction_round)
            .values("percentage_predictions")
            .first()
        )
        percentage_predictions = 0
        if category_data:
            percentage_predictions = category_data["percentage_predictions"]
        if probability is None:
            probability = percentage_predictions
        predictions.append(
            dict(
                id=model_home_bet.id,
                model=model_home_bet.name,
                prediction=prediction,
                prediction_round=prediction_round,
                probability=probability,
                average_predictions=model_home_bet.average_predictions,
                category_percentage=percentage_predictions,
            )
        )
    data = dict(predictions=predictions)
    return data


def generate_model(
    *,
    home_bet_id: int,
    seq_len: int,
    model_type: Optional[ModelType] = ModelType.SEQUENTIAL,
) -> ModelHomeBet | None:
    """
    Generate a model for a home bet
    :param home_bet_id: home bet id
    :param seq_len: sequence length
    :param model_type: model type
    :return: model home bet
    """
    home_bet = core_selectors.filter_home_bet(
        home_bet_id=home_bet_id
    ).first()
    if not home_bet:
        logger.error(
            f"generate_model :: "
            f"home bet {home_bet_id} does not exists"
        )
        return
    # multipliers = core_selectors.get_last_multipliers(home_bet_id=home_bet_id)
    multipliers = core_selectors.get_today_multipliers(home_bet_id=home_bet_id)
    if not multipliers:
        logger.warning(
            f"generate_model :: "
            f"no multipliers for home bet {home_bet_id}"
        )
        return

    name, metrics = prediction_services.create_model(
        home_bet_id=home_bet_id,
        multipliers=multipliers,
        model_type=model_type,
        seq_len=seq_len,
    )
    model_home_bet = create_model_home_bet(
        home_bet=home_bet,
        name=name,
        model_type=model_type,
        seq_len=seq_len,
        others=dict(
            num_multipliers_to_train=len(multipliers),
            # metrics=json.dumps(metrics),
            metrics=metrics,
        ),
    )
    generate_category_result_of_model(model_home_bet=model_home_bet)
    return model_home_bet


def generate_model_for_in_play_home_bet(
    *,
    home_bet_ids: Optional[set[int]] = None,
) -> list[ModelHomeBet]:
    """
    generate model for all in-play home bets
    (multipliers created no more than 10 minutes ago)
    """
    if not home_bet_ids:
        home_bet_ids = core_selectors.filter_home_bet_in_play().values_list(
            "id", flat=True
        )
    models = []
    for home_bet_id in home_bet_ids:
        bets_mod = selectors.get_bets_models_by_average_predictions(
            home_bet_id=home_bet_id, number_of_models=1
        ).first()
        if bets_mod and bets_mod.average_predictions >= PERCENTAGE_ACCEPTABLE:
            continue
        num_multipliers_train = bets_mod.others["num_multipliers_to_train"]
        num_multipliers = core_selectors.count_home_bet_multipliers(
            home_bet_id=home_bet_id
        )
        diff_multipliers = num_multipliers - num_multipliers_train
        if diff_multipliers < DIFF_MULTIPLIERS_TO_GENERATE_NEW_MODEL:
            logger.info(
                f"generate_model_for_in_play_home_bet :: "
                f"home bet {home_bet_id} has {diff_multipliers} "
                f"multipliers to train, skip"
            )
            continue
        for model_type_ in GENERATE_AUTOMATIC_MODEL_TYPES:
            model = generate_model(
                home_bet_id=home_bet_id,
                seq_len=DEFAULT_SEQ_LEN,
                model_type=ModelType(model_type_),
            )
            models.append(model)
            logger.info(
                f"generate_model_for_in_play_home_bet :: "
                f"model {model.id} ({model_type_}) created"
            )
    return models


def generate_category_results_of_models():
    """
    generate category results for all models
    inactive models with average predictions < PERCENTAGE_MODEL_TO_INACTIVE
    """
    models = selectors.filter_models_to_generate_category_result()
    models_to_inactive = []

    for model in models:
        generate_category_result_of_model(model_home_bet=model)
        model.refresh_from_db()
        if model.average_predictions < PERCENTAGE_MODEL_TO_INACTIVE:
            models_to_inactive.append(model)
    if not models_to_inactive:
        return
    home_bet_ids_to_create = {
        model.home_bet_id for model in models_to_inactive
    }
    model_ids_to_inactive = {model.id for model in models_to_inactive}
    # get all models from homes bet to create
    models_ = selectors.filter_model_home_bet(
        home_bet_id__in=home_bet_ids_to_create,
        status=ModelStatus.ACTIVE.value,
    ).values("id", "home_bet_id")
    # home_bet_ids with active models
    home_bet_ids_with_active_model = {
        model["home_bet_id"]
        for model in models_
        if model['id'] not in model_ids_to_inactive
    }
    # get home_bet_ids with no active models
    home_bet_ids_with_no_active_model = set(
        _id for _id in home_bet_ids_to_create
        if _id not in home_bet_ids_with_active_model
    )
    if home_bet_ids_with_no_active_model:
        # create models for home bets with no active models
        generate_model_for_in_play_home_bet(home_bet_ids=home_bet_ids_with_no_active_model)
    # inactive models
    ModelHomeBet.objects.filter(id__in=model_ids_to_inactive).update(
        status=ModelStatus.INACTIVE.value,
    )


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


def get_active_bots(
    *,
    bot_id: Optional[int] = None,
    bot_type: Optional[str] = None,
) -> list[dict[str, any]]:
    bots = selectors.filter_bot(
        bot_id=bot_id,
        bot_type=bot_type,
        is_active=True,
    )
    bots_data = []
    for bot in bots:
        strategies = bot.strategies.filter(
            is_active=True
        ).order_by("number_of_bets", "profit_percentage")
        bots_data.append(dict(
            id=bot.id,
            name=bot.name,
            bot_type=bot.bot_type,
            risk_factor=bot.risk_factor,
            min_multiplier_to_bet=bot.min_multiplier_to_bet,
            min_multiplier_to_recover_losses=bot.min_multiplier_to_recover_losses,
            min_probability_to_bet=bot.min_probability_to_bet,
            min_category_percentage_to_bet=bot.min_category_percentage_to_bet,
            min_category_percentage_value_in_live_to_bet=bot.min_category_percentage_value_in_live_to_bet,
            min_average_prediction_model_in_live_to_bet=bot.min_average_prediction_model_in_live_to_bet,
            stop_loss_percentage=bot.stop_loss_percentage,
            take_profit_percentage=bot.take_profit_percentage,
            strategies=[
                dict(
                    number_of_bets=strategy.number_of_bets,
                    profit_percentage=strategy.profit_percentage,
                    min_amount_percentage_to_bet=strategy.min_amount_percentage_to_bet,
                    profit_percentage_to_bet=strategy.profit_percentage_to_bet,
                    others=strategy.others,
                ) for strategy in strategies
            ]
        ))
    return bots_data
