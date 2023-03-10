# Standard Library
import os
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

# Libraries
import numpy as np
from keras.models import load_model


@dataclass
class _CategoryData:
    count: int
    correct_predictions: int
    incorrect_predictions: int
    percentage_predictions: Decimal
    correct_bets: int
    incorrect_bets: int
    percentage_bets: Decimal
    other_info: Optional[dict] = None


@dataclass
class AverageInfo:
    average_predictions: Decimal
    average_bets: Decimal
    categories_data: dict[int, _CategoryData]


class ModelPredictor:
    def __init__(self, *, model_path: str):
        self.loaded_model = load_model(model_path)
        base_name = os.path.basename(model_path)
        self.length_window = int(base_name.split("_")[2])
        self.average_info = AverageInfo(
            average_predictions=Decimal(0),
            average_bets=Decimal(0),
            categories_data={},
        )

    def predict(self, *, data: list[int]) -> Decimal:
        next_num = self.loaded_model.predict(
            np.array([data[-self.length_window:]])
        )[0][0]
        return round(next_num, 2)

    def evaluate(self, *, data: list[int]) -> AverageInfo:
        X = np.array(# NOQA
            [
                data[i: i + self.length_window]
                for i in range(len(data) - self.length_window)
            ]
        )
        for i in range(len(X)):
            if i == len(X) - 1:
                break
            _data = X[i]
            next_value = X[i + 1][-1]
            value = self.predict(data=_data)
            value_round = round(value, 0)
            category_data = self.average_info.categories_data.get(
                next_value,
                _CategoryData(
                    count=0,
                    correct_predictions=0,
                    incorrect_predictions=0,
                    percentage_predictions=Decimal(0),
                    correct_bets=0,
                    incorrect_bets=0,
                    percentage_bets=Decimal(0),
                ),
            )
            # if value < 1:
            #     value = 1
            # if value < 1:
            #     value = 1
            category_data.count += 1
            if value_round == next_value:
                category_data.correct_predictions += 1
            else:
                category_data.incorrect_predictions += 1
            if value <= next_value:
                category_data.correct_bets += 1
            else:
                category_data.incorrect_bets += 1
            self.average_info.categories_data[next_value] = category_data
        sum_percentage_predictions = 0
        sum_percentage_bets = 0
        count_categories = 0
        for key, value in self.average_info.categories_data.items():
            count_categories += 1
            dict_value = value
            dict_value.average_predictions = round(
                (dict_value.correct_predictions / dict_value.count) * 100, 2
            )
            dict_value.percentage_bets = round(
                (dict_value.correct_bets / dict_value.count) * 100, 2
            )
            dict_value.percentage_predictions = Decimal(
                dict_value.percentage_predictions
            )
            dict_value.average_bets = Decimal(dict_value.average_bets)
            sum_percentage_predictions += dict_value.percentage_predictions
            sum_percentage_bets += dict_value.percentage_bets
            self.average_info.categories_data[key] = dict_value
        self.average_info.average_predictions = round(
            sum_percentage_predictions / count_categories, 2
        )
        self.average_info.average_predictions = Decimal(
            self.average_info.average_predictions
        )
        self.average_info.average_bets = round(
            sum_percentage_bets / count_categories, 2
        )
        self.average_info.average_bets = Decimal(
            self.average_info.average_bets
        )
        return self.average_info
