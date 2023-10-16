# Standard Library
import logging
import os
from decimal import Decimal
from typing import Optional, Tuple

# Internal
from apps.django_projects.predictions.constants import DEFAULT_SEQ_LEN
from apps.django_projects.predictions.models import ModelHomeBet
from apps.prediction.constants import MODELS_PATH, S3_BUCKET_MODELS, ModelType
from apps.prediction.models.base import AverageInfo, PredictionData
from apps.prediction.models.main import CoreModel
from apps.utils.aws import s3

logger = logging.getLogger(__name__)


def upload_model_to_s3(*, model_path: str, model_name: str) -> None:
    """
    Uploads a model to S3
    """
    if not S3_BUCKET_MODELS:
        logger.error("S3_BUCKET_MODELS is not set")
        return
    s3.upload_file_to_s3(
        file_path=model_path,
        bucket_name=S3_BUCKET_MODELS,
        key=model_name,
    )


def download_model_from_s3(
    *,
    model_name: str,
) -> bool:
    """
    Downloads a model from S3
    if it does not exist in MODELS_PATH
    """
    if not S3_BUCKET_MODELS:
        logger.error("download_model_from_s3 :: S3_BUCKET_MODELS is not set")
        return False
    # validate if model_name already exists in MODELS_PATH
    model_path = f"{MODELS_PATH}/{model_name}"
    if os.path.exists(model_path):
        logger.info(
            f"download_model_from_s3 :: Model {model_name} "
            f"already exists in {model_path}"
        )
        return True
    s3.download_file_from_s3(
        bucket_name=S3_BUCKET_MODELS,
        key=model_name,
        file_path=model_path,
    )


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
    model_path, metrics = core_model.train(
        home_bet_id=home_bet_id,
        multipliers=multipliers,
    )
    name = os.path.basename(model_path)
    upload_model_to_s3(
        model_path=model_path,
        model_name=name,
    )
    return name, metrics


def predict(
    *, model_home_bet: ModelHomeBet, multipliers: list[Decimal]
) -> PredictionData:
    """
    Predicts the next multiplier
    @param model_home_bet: The model home bet
    @param multipliers: The multipliers to predict the next multiplier
    @return: The next multiplier
    """
    model = CoreModel(model_home_bet=model_home_bet)
    prediction_data = model.predict(multipliers=multipliers)
    return prediction_data


def evaluate_model_home_bet(
    *,
    model_home_bet: ModelHomeBet,
    multipliers: list[Decimal],
    probability_to_eval: Optional[float] = None,
) -> AverageInfo:
    """
    Evaluates a model home bet
    @param model_home_bet: The model home bet
    @param multipliers: The multipliers to evaluate the model home bet
    @param probability_to_eval: The probability to evaluate the model home bet
    @return: The average info
    """
    model = CoreModel(model_home_bet=model_home_bet)
    average_info = model.evaluate(
        multipliers=multipliers, probability_to_eval=probability_to_eval
    )
    return average_info


def remove_model_file(*, name: str) -> None:
    """
    Removes a model file
    @param name: The name of the model file
    """
    path = f"{MODELS_PATH}{name}"
    os.path.isfile(path=path) and os.remove(path=path)
    # delete model from s3
    s3.delete_file_from_s3(
        bucket_name=S3_BUCKET_MODELS,
        key=name,
    )
