# Standard Library
import logging
from datetime import datetime
from decimal import Decimal
from operator import itemgetter
from typing import Optional

# Django
from django.db.models import Max
from rest_framework.exceptions import ValidationError

# Internal
from apps.django_projects.core import selectors as core_selectors
from apps.django_projects.core.models import HomeBet, HomeBetGame
from apps.django_projects.predictions import selectors
from apps.django_projects.predictions.constants import (
    DEFAULT_SEQ_LEN,
    DIFF_MULTIPLIERS_TO_GENERATE_NEW_MODEL,
    GENERATE_AUTOMATIC_MODEL_TYPES,
    MIN_MULTIPLIERS_TO_GENERATE_MODEL,
    NUMBER_OF_MULTIPLIERS_TO_EVALUATE_MODEL,
    PERCENTAGE_ACCEPTABLE,
    PERCENTAGE_MODEL_TO_INACTIVE,
    ModelStatus,
)
from apps.django_projects.predictions.models import (
    ModelDetail,
    ModelHomeBetGame,
)
from apps.prediction import services as prediction_services
from apps.prediction.constants import ModelType

logger = logging.getLogger(__name__)


def create_model_home_bet(
    *,
    home_bet_game: HomeBetGame,
    name: str,
    model_type: ModelType,
    seq_len: int,
    others: Optional[dict] = {},
) -> ModelHomeBetGame:
    model = ModelHomeBetGame.objects.create(
        home_bet_game=home_bet_game,
        name=name,
        model_type=model_type.value,
        seq_len=seq_len,
        others=others,
    )
    return model


def create_model_detail(
    *,
    model_home_bet_game_id: int,
    category: int,
    correct_predictions: int,
    incorrect_predictions: int,
    percentage_predictions: float,
    correct_bets: int,
    incorrect_bets: int,
    percentage_bets: float,
    other_info: Optional[dict] = {},
) -> ModelDetail:
    model = selectors.filter_model_home_bet_by_id(
        model_home_bet_game_id=model_home_bet_game_id
    ).first()
    if not model:
        raise ValidationError(
            f"create_model_average_result :: "
            f"model home bet game {model_home_bet_game_id} does not exists"
        )
    average = ModelDetail.objects.create(
        model_home_bet_game_id=model_home_bet_game_id,
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


def generate_details_of_model(
    *,
    model_home_bet_game: ModelHomeBetGame,
    count_multipliers: Optional[int] = None,
) -> None:
    model_home_bet_game_id = model_home_bet_game.id
    print("---------------------------------------------------------")
    print(f"generation category result for model {model_home_bet_game_id}")
    print("---------------------------------------------------------")
    now = datetime.now()
    count_multipliers = (
        count_multipliers or NUMBER_OF_MULTIPLIERS_TO_EVALUATE_MODEL
    )
    multipliers = core_selectors.get_last_multipliers(
        home_bet_game_id=model_home_bet_game_id, count=count_multipliers
    )
    average_result = prediction_services.evaluate_model_home_bet(
        model_home_bet=model_home_bet_game, multipliers=multipliers
    )
    # save total averages
    model_home_bet_game.result_date = now
    model_home_bet_game.average_predictions = (
        average_result.average_predictions
    )
    model_home_bet_game.average_bets = average_result.average_bets
    model_home_bet_game.save()
    for key, value in average_result.categories_data.items():
        category_ = model_home_bet_game.details.filter(category=key).first()
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
        create_model_detail(
            model_home_bet_game_id=model_home_bet_game_id,
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
    home_bet_game_id: int,
    multipliers: Optional[list[Decimal]] = None,
    model_home_bet_id: Optional[int] = None,
) -> dict:
    models = selectors.get_bets_models_by_average_predictions(
        home_bet_game_id=home_bet_game_id,
        model_home_bet_id=model_home_bet_id,
    )
    if not models:
        raise ValidationError("no models")
    if not multipliers:
        max_ = models.aggregate(max=Max("seq_len"))["max"]
        multipliers = core_selectors.get_last_multipliers(
            home_bet_game_id=home_bet_game_id, count=max_
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
            model_home_bet.details.filter(category=prediction_round)
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
    home_bet_game_id: int,
    seq_len: int,
    model_type: Optional[ModelType] = ModelType.SEQUENTIAL,
) -> ModelHomeBetGame | None:
    """
    Generate a model for a home bet
    :param home_bet_game_id: home bet id
    :param seq_len: sequence length
    :param model_type: model type
    :return: model home bet
    """
    home_bet_game = core_selectors.filter_home_bet_game_by_id(
        home_bet_game_id=home_bet_game_id
    ).first()
    if not home_bet_game:
        logger.error(
            f"generate_model :: "
            f"home bet {home_bet_game_id} does not exists"
        )
        return

    # USE ALL MULTIPLIERS
    # now = datetime.now().date()
    multipliers = core_selectors.get_last_multipliers(
        home_bet_game_id=home_bet_game_id,
        count=400,
        # filter_=dict(multiplier_dt__date__lt=now),
    )
    if not multipliers:
        logger.warning(
            f"generate_model :: "
            f"no multipliers for home bet {home_bet_game_id}"
        )
        return
    if len(multipliers) < MIN_MULTIPLIERS_TO_GENERATE_MODEL:
        multipliers = core_selectors.get_last_multipliers(
            home_bet_game_id=home_bet_game_id,
            count=MIN_MULTIPLIERS_TO_GENERATE_MODEL,
        )

    name, metrics = prediction_services.create_model(
        home_bet_id=home_bet_game_id,
        multipliers=multipliers,
        model_type=model_type,
        seq_len=seq_len,
    )
    model_home_bet = selectors.filter_model_home_bet_game(
        home_bet_game_id=home_bet_game_id, model_type=model_type
    ).first()
    if not model_home_bet:
        model_home_bet = create_model_home_bet(
            home_bet_game=home_bet_game,
            name=name,
            model_type=model_type,
            seq_len=seq_len,
            others=dict(
                num_multipliers_to_train=len(multipliers),
                metrics=metrics,
            ),
        )
    else:
        old_model_name = model_home_bet.name
        model_home_bet.name = name
        model_home_bet.seq_len = seq_len
        model_home_bet.others = dict(
            num_multipliers_to_train=len(multipliers),
            metrics=metrics,
        )
        model_home_bet.status = ModelStatus.ACTIVE.value
        model_home_bet.save()
        prediction_services.remove_model_file(name=old_model_name)
    generate_details_of_model(model_home_bet_game=model_home_bet)
    return model_home_bet


def generate_model_for_in_play_home_bet_game(
    *,
    home_bet_game_ids: Optional[set[int]] = None,
) -> list[ModelHomeBetGame]:
    """
    generate model for all in-play home bets
    (multipliers created no more than 10 minutes ago)
    """
    if not home_bet_game_ids:
        home_bet_game_ids = (
            core_selectors.filter_home_bet_game_in_play().values_list(
                "id", flat=True
            )
        )
    models = []
    for home_bet_game_id in home_bet_game_ids:
        bets_mod = selectors.get_bets_models_by_average_predictions(
            home_bet_game_id=home_bet_game_id, number_of_models=1
        ).first()
        if bets_mod and bets_mod.average_predictions >= PERCENTAGE_ACCEPTABLE:
            continue
        num_multipliers_train = bets_mod.others["num_multipliers_to_train"]
        num_multipliers = core_selectors.count_home_bet_multipliers(
            home_bet_id=home_bet_game_id
        )
        diff_multipliers = num_multipliers - num_multipliers_train
        if diff_multipliers < DIFF_MULTIPLIERS_TO_GENERATE_NEW_MODEL:
            logger.info(
                f"generate_model_for_in_play_home_bet :: "
                f"home bet {home_bet_game_id} has {diff_multipliers} "
                f"multipliers to train, skip"
            )
            continue
        for model_type_ in GENERATE_AUTOMATIC_MODEL_TYPES:
            model = generate_model(
                home_bet_game_id=home_bet_game_id,
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
        generate_details_of_model(model_home_bet_game=model)
        model.refresh_from_db()
        if model.average_predictions < PERCENTAGE_MODEL_TO_INACTIVE:
            models_to_inactive.append(model)
    if not models_to_inactive:
        return
    home_bet_games_ids_to_create = {
        model.home_bet_game_id for model in models_to_inactive
    }
    model_ids_to_inactive = {model.id for model in models_to_inactive}
    # get all models from homes bet to create
    models_ = selectors.filter_model_home_bet_game(
        home_bet_game_id__in=home_bet_games_ids_to_create,
        status=ModelStatus.ACTIVE.value,
    ).values("id", "home_bet_id")
    # home_bet_ids with active models
    home_bet_ids_with_active_model = {
        model["home_bet_id"]
        for model in models_
        if model["id"] not in model_ids_to_inactive
    }
    # get home_bet_ids with no active models
    home_bet_game_ids_with_no_active_model = set(
        _id
        for _id in home_bet_games_ids_to_create
        if _id not in home_bet_ids_with_active_model
    )
    if home_bet_game_ids_with_no_active_model:
        # create models for home bets with no active models
        models = generate_model_for_in_play_home_bet_game(
            home_bet_game_ids=home_bet_game_ids_with_no_active_model
        )
        for model in models:
            if model.id in model_ids_to_inactive:
                model_ids_to_inactive.remove(model.id)
    # inactive models
    ModelHomeBetGame.objects.filter(id__in=model_ids_to_inactive).update(
        status=ModelStatus.INACTIVE.value,
    )


def get_models_home_bet(
    *, home_bet_game_id: int, status: Optional[str] = ModelStatus.ACTIVE.value
) -> list[dict]:
    home_bet_game_exists = core_selectors.filter_home_bet_game_by_id(
        home_bet_game_id=home_bet_game_id
    ).exists()
    if not home_bet_game_exists:
        raise ValidationError(f"home bet {home_bet_game_id} does not exists")
    models = selectors.filter_model_home_bet_game_by_home_bet_game_id(
        home_bet_game_id=home_bet_game_id, status=status
    ).order_by("-average_predictions")
    data = []
    for model in models:
        categories = []
        for category in model.details.order_by("category"):
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
                home_bet_game_id=model.home_bet_game_id,
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
    print(data)
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
        conditions = bot.conditions.all().order_by("id")
        bots_data.append(
            dict(
                id=bot.id,
                name=bot.name,
                bot_type=bot.bot_type,
                number_of_min_bets_allowed_in_bank=bot.number_of_min_bets_allowed_in_bank,  # noqa
                risk_factor=bot.risk_factor,
                min_multiplier_to_bet=bot.min_multiplier_to_bet,
                min_multiplier_to_recover_losses=bot.min_multiplier_to_recover_losses,  # noqa
                min_probability_to_bet=bot.min_probability_to_bet,
                max_recovery_percentage_on_max_bet=bot.max_recovery_percentage_on_max_bet,  # noqa
                min_category_percentage_to_bet=bot.min_category_percentage_to_bet,  # noqa
                min_average_model_prediction=bot.min_average_model_prediction,
                stop_loss_percentage=bot.stop_loss_percentage,
                take_profit_percentage=bot.take_profit_percentage,
                conditions=[
                    dict(
                        id=condition.id,
                        condition_on=condition.condition_on,
                        condition_on_value=condition.condition_on_value,
                        condition_on_value_2=condition.condition_on_value_2,
                        actions=condition.actions,
                        others=condition.others,
                    )
                    for condition in conditions
                ],
            )
        )
    return bots_data


def evaluate_model(
    *,
    model_home_bet_game_id: int,
    count_multipliers: Optional[int] = None,
    probability_to_eval: Optional[float] = None,
    today_multipliers: Optional[bool] = False,
) -> dict[str, any]:
    model_home_bet = selectors.filter_model_home_bet_by_id(
        model_home_bet_game_id=model_home_bet_game_id
    ).first()
    if not model_home_bet:
        raise ValidationError(
            f"model {model_home_bet_game_id} does not exists"
        )
    print("---------------------------------------------------------")
    print(f"******** evaluating model {model_home_bet_game_id} ************")
    print("---------------------------------------------------------")
    count_multipliers = (
        count_multipliers or NUMBER_OF_MULTIPLIERS_TO_EVALUATE_MODEL
    )
    if today_multipliers:
        multipliers = core_selectors.get_today_multipliers(
            home_bet_game_id=model_home_bet.home_bet_game_id,
        )
    else:
        multipliers = core_selectors.get_last_multipliers(
            home_bet_game_id=model_home_bet.home_bet_game_id,
            count=count_multipliers,
        )
    average_result = prediction_services.evaluate_model_home_bet(
        model_home_bet=model_home_bet,
        multipliers=multipliers,
        probability_to_eval=probability_to_eval,
    )
    category_results = []
    for key, value in average_result.categories_data.items():
        category_results.append(
            dict(
                category=key,
                correct_predictions=value.correct_predictions,
                incorrect_predictions=value.incorrect_predictions,
                percentage_predictions=value.percentage_predictions,
                correct_bets=value.correct_bets,
                incorrect_bets=value.incorrect_bets,
                percentage_bets=value.percentage_bets,
            )
        )
    category_results = sorted(category_results, key=itemgetter("category"))
    data = dict(
        average_predictions=average_result.average_predictions,
        category_results=category_results,
    )
    return data


def get_position_values(
    *, home_bet_game_id: int, multipliers: Optional[list[int]] = None
) -> dict[str, any]:
    """
    Returns the number of positions that each
        value has in the home bet
    dict(
        all_time=dict(
            count=number of positions,
            multipliers=dict(
                multiplier: dict(
                    count: max number of times that
                        the multiplier has been in that position,
                    positions: dict(
                        position: count
                    )
                )
           )
        ),
        today=dict(
            count=number of positions,
            multipliers=dict(
                multiplier: dict(
                    count: max number of times that the
                        multiplier has been in that position,
                    positions: dict(
                        position: count
                    )
                )
           )
        )
    )
    """

    def count_positions(
        multipliers_: list[Decimal],
        threshold: float,
        next_threshold: Optional[float] = None,
    ):
        count = 0
        if not multipliers_:
            return None
        data_ = {}
        position = 0
        for num in multipliers_:
            position += 1
            next_threshold = next_threshold or num + Decimal(0.01)
            # if threshold <= num < next_threshold:
            if threshold <= num:
                count += 1
                if position in data_:
                    data_[position] += 1
                else:
                    data_[position] = 1
                position = 0
        return dict(count=count, positions=dict(sorted(data_.items())))

    values = multipliers or [2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 50, 100]
    # values = multipliers or [2]
    all_multipliers = core_selectors.get_last_multipliers(
        home_bet_game_id=home_bet_game_id
    )
    today_multipliers = core_selectors.get_today_multipliers(
        home_bet_game_id=home_bet_game_id
    )
    if not all_multipliers:
        raise ValidationError(
            f"home bet game {home_bet_game_id} does not have multipliers"
        )
    data = dict(
        all_time=dict(),
    )
    if today_multipliers:
        data["today"] = dict()
    for i in range(len(values)):
        data["all_time"][values[i]] = count_positions(
            all_multipliers, values[i]
        )
        if not today_multipliers:
            continue
        data["today"][values[i]] = count_positions(
            today_multipliers,
            values[i],
        )
    return data


def download_models_from_s3() -> None:
    """
    Download all active models from s3
    """
    active_model_names = selectors.filter_model_home_bet_game(
        status=ModelStatus.ACTIVE.value,
    ).values_list("name", flat=True)
    if not active_model_names:
        logger.info("download_models_from_s3 :: no active models")
        return
    for model_name in active_model_names:
        # validate if model exists
        prediction_services.download_model_from_s3(
            model_name=model_name,
        )
