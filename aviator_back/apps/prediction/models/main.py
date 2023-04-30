# Standard Library
from decimal import Decimal
from typing import Optional, Tuple

# Libraries
from apps.django_projects.predictions.constants import DEFAULT_SEQ_LEN
from apps.django_projects.predictions.models import ModelHomeBet
from apps.prediction import utils
from apps.prediction.constants import ModelType
from apps.prediction.models.base import (
    AbstractBaseModel,
    AverageInfo,
    PredictionData,
)
from apps.prediction.models.gru_model import GRUModel
from apps.prediction.models.sequential_model import SequentialModel
from apps.prediction.models.transformer_model import TransformerModel


class CoreModel:
    """
    Core model class. This class is used to
    encapsulate all models available in the app
    """

    def __init__(
        self,
        *,
        model_home_bet: Optional[ModelHomeBet] = None,
        model_type: Optional[ModelType] = None,
        seq_len: Optional[int] = DEFAULT_SEQ_LEN,
    ):
        if model_home_bet is None and model_type is None:
            raise ValueError("model_home_bet or model_type must be provided")
        self.model_home_bet = model_home_bet
        self.model_type = (
            ModelType(self.model_home_bet.model_type)
            if self.model_home_bet
            else model_type
        )
        self.seq_len = (
            self.model_home_bet.seq_len if self.model_home_bet else seq_len
        )
        self.model = self.__get_model(seq_len=self.seq_len)
        if self.model_home_bet:
            self.model.load_model(name=self.model_home_bet.name)

    def __get_model(self, *, seq_len: int) -> AbstractBaseModel:
        match self.model_type:
            case ModelType.SEQUENTIAL:
                model = SequentialModel(
                    model_type=ModelType.SEQUENTIAL, seq_len=seq_len
                )
            case ModelType.SEQUENTIAL_LSTM:
                model = SequentialModel(
                    model_type=ModelType.SEQUENTIAL_LSTM, seq_len=seq_len
                )
            case ModelType.GRU:
                model = GRUModel(model_type=ModelType.GRU, seq_len=seq_len)
            case ModelType.TRANSFORMER:
                model = TransformerModel(seq_len=seq_len)
            case _:
                raise ValueError(
                    f"model_type: {self.model_type} is not supported"
                )
        return model

    def train(
        self,
        *,
        home_bet_id: int,
        multipliers: list[Decimal],
        test_size: Optional[float] = 0.2,
        epochs: Optional[int] = None,
    ) -> Tuple[str, dict]:
        """
        Trains a model and returns the path to the model and the loss
        @param home_bet_id: The id of the home bet
        @param multipliers: The multipliers to train the model on
        @param test_size: The size of the test data
        @param epochs: The number of epochs to train the model
        @return: The name to the model and the loss error and accurracy
        """
        return self.model.train(
            home_bet_id=home_bet_id,
            multipliers=multipliers,
            test_size=test_size,
            epochs=epochs,
        )

    def evaluate(
        self,
        *,
        multipliers: list[Decimal],
        probability_to_eval: Optional[float] = None,
    ) -> AverageInfo:
        """
        Evaluates the model
        @param multipliers: The multipliers to evaluate the model on
        @param probability_to_eval: The probability to evaluate the model on
        @return: The average info
        """
        assert (
            self.model_home_bet is not None
        ), "model_home_bet must be provided"
        return self.model.evaluate(
            multipliers=multipliers, probability_to_eval=probability_to_eval
        )

    def predict(self, *, multipliers: list[Decimal]) -> PredictionData:
        """
        Predicts the next multiplier
        @param multipliers: The data to predict the next multiplier on
        @return: The next multiplier
        """
        assert (
            self.model_home_bet is not None
        ), "model_home_bet must be provided"
        data = utils.transform_multipliers_to_data(multipliers=multipliers)
        return self.model.predict(data=data)
