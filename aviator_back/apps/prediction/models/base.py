# Standard Library
import abc
import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Tuple

# Libraries
import numpy as np

# Internal
from apps.django_projects.predictions.constants import DEFAULT_SEQ_LEN
from apps.prediction import utils
from apps.prediction.constants import MODELS_PATH, Category, ModelType


@dataclass
class _CategoryData:
    count: int
    correct_predictions: int
    incorrect_predictions: int
    percentage_predictions: float
    correct_bets: int
    incorrect_bets: int
    percentage_bets: float
    other_info: Optional[dict] = None


@dataclass
class AverageInfo:
    average_predictions: float
    average_bets: float
    categories_data: dict[int, _CategoryData]


class AbstractBaseModel(abc.ABC):
    """
    Abstract class for the models
    """

    MODEL_EXTENSION = "h5"

    def __init__(
        self,
        *,
        model_type: ModelType,
        seq_len: Optional[int] = DEFAULT_SEQ_LEN,
    ):
        self.model_type = model_type
        self.seq_len = seq_len
        self.average_info = AverageInfo(
            average_predictions=0,
            average_bets=0,
            categories_data={},
        )
        self.model = None

    @abc.abstractmethod
    def _compile_model(self) -> any:
        ...

    def _split_data_to_train(
        self, data: list[int]
    ) -> Tuple[np.array, np.array]:
        """
        get the list of sequences and the list of next values
        @return: Tuple[train_data, test_data]
        the list of sequences and the list of next values
        """
        X = np.array(  # NOQA
            [
                data[i: i + self.seq_len]
                for i in range(len(data) - self.seq_len)
            ]
        )
        y = np.array(data[self.seq_len:])
        return X, y

    @abc.abstractmethod
    def load_model(self, *, name: str) -> None:
        ...

    @abc.abstractmethod
    def train(
        self,
        *,
        home_bet_id: int,
        multipliers: list[Decimal],
        test_size: Optional[float] = 0.2,
        epochs: Optional[int] = None,
    ) -> Tuple[str, float]:
        """
        train the model
        @param home_bet_id: the home bet id
        @param multipliers: list of multipliers
        @param test_size: the test size
        @param epochs: the number of epochs
        @return: model_name, loss
        """
        ...

    @abc.abstractmethod
    def predict(self, *, data: list[int]) -> Decimal:
        ...

    def _generate_model_path_to_save(
        self, *, home_bet_id: int
    ) -> Tuple[str, str]:
        """
        generate the model path
        @param home_bet_id: the home bet id
        @return: model_name, model_path
        """
        name = f"{home_bet_id}_{uuid.uuid4()}.{self.MODEL_EXTENSION}"
        model_path = f"{MODELS_PATH}{name}"
        return name, model_path

    def _get_model_path(self, *, name: str) -> str:
        """
        get the model path
        @param name: the model home bet name
        @return: model_path
        """
        return f"{MODELS_PATH}{name}"

    def evaluate(self, *, multipliers: list[Decimal]) -> AverageInfo:
        """
        evaluate the model
        @param multipliers: list of multipliers in Decimal value
        @return: AverageInfo
        """
        data = utils.transform_multipliers_to_data(multipliers=multipliers)
        X, y = self._split_data_to_train(data)  # NOQA
        y_multiplier = np.array(multipliers[self.seq_len:])
        for i in range(len(X)):
            if i == len(X) - 1:
                break
            _data = X[i]
            next_value = y[i]
            next_multiplier = y_multiplier[i]
            value = self.predict(data=_data)
            value_round = round(value, 0)
            category_data = self.average_info.categories_data.get(
                next_value,
                _CategoryData(
                    count=0,
                    correct_predictions=0,
                    incorrect_predictions=0,
                    percentage_predictions=0,
                    correct_bets=0,
                    incorrect_bets=0,
                    percentage_bets=0,
                ),
            )
            if value < 1:
                value = 1
            if value > 3:
                value = 3
            category_data.count += 1
            if value_round == next_value:
                category_data.correct_predictions += 1
            else:
                category_data.incorrect_predictions += 1
            if value <= next_multiplier:
                category_data.correct_bets += 1
            else:
                category_data.incorrect_bets += 1
            self.average_info.categories_data[next_value] = category_data
        sum_percentage_predictions = 0
        sum_percentage_bets = 0
        count_categories = 0
        for key, value in self.average_info.categories_data.items():
            dict_value = value
            dict_value.percentage_predictions = utils.to_float(
                (dict_value.correct_predictions / dict_value.count) * 100
            )
            dict_value.percentage_bets = utils.to_float(
                (dict_value.correct_bets / dict_value.count) * 100
            )
            if key == Category.CATEGORY_3.value:
                continue
            count_categories += 1
            sum_percentage_predictions += dict_value.percentage_predictions
            sum_percentage_bets += dict_value.percentage_bets
            self.average_info.categories_data[key] = dict_value
        self.average_info.average_predictions = utils.to_float(
            sum_percentage_predictions / count_categories
        )
        self.average_info.average_bets = utils.to_float(
            sum_percentage_bets / count_categories
        )
        return self.average_info
