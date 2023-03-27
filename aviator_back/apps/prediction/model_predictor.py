# Standard Library
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

# Libraries
import numpy as np
from keras.models import load_model

# Internal
from apps.prediction import utils
from apps.prediction.constants import Category


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


class ModelPredictor:
    def __init__(self, *, model_path: str, seq_len: int):
        self.loaded_model = load_model(model_path)
        self.seq_len = seq_len
        self.average_info = AverageInfo(
            average_predictions=0,
            average_bets=0,
            categories_data={},
        )

    def predict(self, *, data: list[int]) -> Decimal:
        """
        predict the nex multiplier
        @param data: list of multipliers transformed to categorize
        @return: the next multiplier
        """
        next_num = self.loaded_model.predict(
            np.array([data[-self.seq_len:]])
        )[0][0]
        return round(next_num, 2)

    def evaluate(self, *, multipliers: list[Decimal]) -> AverageInfo:
        """
        evaluate the model
        @param multipliers: list of multipliers in Decimal value
        @return: AverageInfo
        """
        data = utils.transform_multipliers_to_data(multipliers=multipliers)
        X = np.array(  # NOQA
            [
                data[i: i + self.seq_len]
                for i in range(len(data) - self.seq_len)
            ]
        )
        y = np.array(data[self.seq_len:])
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
            if value < 1:
                value = 1
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
