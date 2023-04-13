# Standard Library
from decimal import Decimal
from typing import Optional, Tuple

# Libraries
import numpy as np

# Internal
from apps.django_projects.core import selectors as core_selectors
from apps.django_projects.predictions.constants import DEFAULT_SEQ_LEN
from apps.django_projects.predictions.models import ModelHomeBet
from apps.prediction import utils
from apps.prediction.constants import DATA_EXPORT_PATH, ModelType
from apps.prediction.model_predictor import AverageInfo
from apps.prediction.models.main import CoreModel


def create_model(
    *,
    home_bet_id: int,
    multipliers: list[Decimal],
    model_type: ModelType,
    seq_len: Optional[int] = DEFAULT_SEQ_LEN,
) -> Tuple[str, dict]:
    """
    Creates a model
    @param home_bet_id: The id of the home bet
    @param multipliers: The multipliers to train the model on
    @param model_type: The type of the model
    @param seq_len: The sequence length of the model
    @return: The name to the model and the loss error and accuracy
    """
    core_model = CoreModel(model_type=model_type, seq_len=seq_len)
    name, metrics = core_model.train(
        home_bet_id=home_bet_id,
        multipliers=multipliers,
    )
    return name, metrics


def predict(
    *, model_home_bet: ModelHomeBet, multipliers: list[Decimal]
) -> Decimal:
    """
    Predicts the next multiplier
    @param model_home_bet: The model home bet
    @param multipliers: The multipliers to predict the next multiplier
    @return: The next multiplier
    """
    model = CoreModel(model_home_bet=model_home_bet)
    prediction = model.predict(multipliers=multipliers)
    return prediction


def evaluate_model_home_bet(
    *, model_home_bet: ModelHomeBet, multipliers: list[Decimal]
) -> AverageInfo:
    """
    Evaluates a model home bet
    @param model_home_bet: The model home bet
    @param multipliers: The multipliers to evaluate the model home bet
    @return: The average info
    """
    model = CoreModel(model_home_bet=model_home_bet)
    average_info = model.evaluate(multipliers=multipliers)
    return average_info


def extract_multipliers_to_csv(*, home_bet_id: int, convert_to_data: Optional[bool] = False) -> str:
    data = core_selectors.get_last_multipliers(home_bet_id=home_bet_id)
    if convert_to_data:
        data = utils.transform_multipliers_to_data(data)
    file_path = f"{DATA_EXPORT_PATH}data_{home_bet_id}_{len(data)}.csv"
    np.savetxt(
        file_path,
        data,
        delimiter=", ",
        fmt="% s",
    )
    return file_path
