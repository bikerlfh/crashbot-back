import os
import numpy as np
from keras.models import load_model
from decimal import Decimal


class SequentialPrediction:
    def __init__(self, *, model_path: str):
        self.loaded_model = load_model(model_path)
        base_name = os.path.basename(model_path)
        self.length_window = int(base_name.split("_")[2])
        self.average_info = {}

    def predict(
        self,
        *,
        data: list[int]
    ) -> Decimal:
        next_num = self.loaded_model.predict(np.array([data[-self.length_window:]]))[0][0]
        return round(next_num, 2)

    def evaluate(self, *, data: list[int]):
        X = np.array([ # NOQA
            data[i:i + self.length_window]
            for i in range(len(data) - self.length_window)
        ])
        for i in range(len(X)):
            if i == len(X) - 1:
                break
            _data = X[i]
            next_value = X[i + 1][-1]
            value = self.predict(data=_data)
            value_round = round(value, 0)
            dict_value = self.average_info.get(
                next_value, dict(
                    count=0,
                    correct=0,
                    incorrect=0,
                    percentage=0,
                    correct_bet=0,
                    incorrect_bet=0
                )
            )
            # if value < 1:
            #     value = 1
            # if value < 1:
            #     value = 1
            dict_value["count"] += 1
            if value_round == next_value:
                dict_value["correct"] += 1
            else:
                dict_value["incorrect"] += 1
            if value <= next_value:
                dict_value["correct_bet"] += 1
            else:
                dict_value["incorrect_bet"] += 1
            self.average_info[next_value] = dict_value
        for key, value in self.average_info.items():
            dict_value = value
            dict_value["percentage"] = round(
                (dict_value["correct"] / dict_value["count"]) * 100, 2
            )
            self.average_info[key] = dict_value
        return self.average_info
