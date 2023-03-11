# Standard Library
from typing import Tuple
from decimal import Decimal

# Libraries
import numpy as np

# Internal
from apps.django_projects.core import selectors as core_selectors
from apps.django_projects.predictions.models import ModelHomeBet
from apps.prediction import train_models, utils
from apps.prediction.constants import DATA_EXPORT_PATH, MODELS_PATH
from apps.prediction.model_predictor import AverageInfo, ModelPredictor


def predict(
    *, model_home_bet: ModelHomeBet, multipliers: list[Decimal]
) -> Decimal:
    model_path = f"{MODELS_PATH}{model_home_bet.name}"
    model = ModelPredictor(model_path=model_path, seq_len=model_home_bet.seq_len)
    data = utils.transform_multipliers_to_data(multipliers=multipliers)
    prediction = model.predict(data=data)
    return prediction


def evaluate_model_home_bet(
    *, model_home_bet: ModelHomeBet, multipliers: list[Decimal]
) -> AverageInfo:
    model_path = f"{MODELS_PATH}{model_home_bet.name}"
    model = ModelPredictor(model_path=model_path, seq_len=model_home_bet.seq_len)
    data = utils.transform_multipliers_to_data(multipliers=multipliers)
    average_info = model.evaluate(data=data)
    return average_info


def extract_multipliers_to_csv(*, home_bet_id: int):
    multipliers = core_selectors.get_last_multipliers(home_bet_id=home_bet_id)
    data = utils.transform_multipliers_to_data(multipliers)
    np.savetxt(
        f"{DATA_EXPORT_PATH}data_{home_bet_id}_{len(data)}.csv",
        data,
        delimiter=", ",
        fmt="% s",
    )


def create_sequential_model(
    *,
    home_bet_id: int,
    multipliers: list[Decimal],
    seq_len: int,
) -> Tuple[str, float]:
    data = utils.transform_multipliers_to_data(multipliers)
    name, eval_error = train_models.create_sequential_model(
        home_bet_id=home_bet_id,
        data=data,
        seq_len=seq_len,
    )
    return name, eval_error


def create_sequential_lstm_model(
    *,
    home_bet_id: int,
    multipliers: list[Decimal],
    seq_len: int,
) -> Tuple[str, float]:
    data = utils.transform_multipliers_to_data(multipliers)
    name, eval_error = train_models.create_sequential_lstm_model(
        home_bet_id=home_bet_id,
        data=data,
        seq_len=seq_len,
    )
    return name, eval_error
