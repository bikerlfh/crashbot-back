# Standard Library
import os
from decimal import Decimal
from typing import Optional, Tuple

# Libraries
import numpy as np
from keras.layers import LSTM, Dense, Dropout
from keras.models import Sequential, load_model
from sklearn.model_selection import train_test_split
from apps.django_projects.predictions.constants import DEFAULT_SEQ_LEN
from apps.prediction.constants import (
    ModelType,
    Category,
    MIN_PROBABILITY_TO_EVALUATE_MODEL
)
from apps.prediction.models.base import AbstractBaseModel, PredictionData, CategoryData, AverageInfo
from apps.prediction.models.constants import EPOCHS_SEQUENTIAL, EPOCHS_SEQUENTIAL_LSTM
from apps.prediction import utils


class SequentialModel(AbstractBaseModel):
    """
    sequential model class
    not use directly. Use CoreModel instead
    """
    APPLY_MIN_PROBABILITY = True
    MODEL_EXTENSION = "h5"

    def __init__(
        self,
        *,
        model_type: ModelType,
        seq_len: Optional[int] = DEFAULT_SEQ_LEN,
    ):
        self._epochs = 2500
        super(SequentialModel, self).__init__(
            model_type=model_type, seq_len=seq_len
        )

    def _compile_model(self) -> Sequential:
        model = Sequential()
        match self.model_type:
            case ModelType.SEQUENTIAL:
                model.add(Dense(64, input_dim=self.seq_len, activation="relu"))
                model.add(Dense(32, activation="relu"))
                model.add(Dropout(0.2))
                model.add(Dense(16, activation="relu"))
                model.add(Dense(1))
                self._epochs = EPOCHS_SEQUENTIAL
            case ModelType.SEQUENTIAL_LSTM:
                model.add(LSTM(units=32, input_shape=(self.seq_len, 1)))
                model.add(Dense(units=1))
                self._epochs = EPOCHS_SEQUENTIAL_LSTM
            case _:
                raise ValueError("Invalid model type")
        model.compile(loss="mse", optimizer="adam")
        return model

    def train(
        self,
        *,
        home_bet_id: int,
        multipliers: list[Decimal],
        test_size: Optional[float] = 0.2,
        epochs: Optional[int] = None,
    ) -> Tuple[str, dict]:
        data = utils.transform_multipliers_to_data(multipliers)
        self._epochs = epochs or self._epochs
        X, y = self._split_data_to_train(data=data)  # NOQA
        X_train, X_test, y_train, y_test = train_test_split(  # NOQA
            X, y, test_size=test_size, random_state=42
        )
        model = self._compile_model()
        model.fit(X_train, y_train, epochs=self._epochs, batch_size=32)
        lost = model.evaluate(X_test, y_test)
        name, model_path = self._generate_model_path_to_save(
            home_bet_id=home_bet_id
        )
        model.save(model_path)
        metrics = dict(
            lost=lost,
        )
        print("---------------------------------------------")
        print(f"--------MODEL: {name} ERROR: {lost}----------")
        print("---------------------------------------------")
        return name, metrics

    def load_model(self, *, name: str) -> None:
        model_path = self._get_model_path(name=name)
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"file not found'{model_path}'")
        self.model = load_model(model_path)

    def predict(self, *, data: list[int]) -> PredictionData:
        next_num = self.model.predict(np.array([data[-self.seq_len:]]))[0][0]
        prediction = round(next_num, 2)
        # TODO: refactor if the categories change. this is only for 1 and 2
        prediction_round = 2 if prediction > 1 else 1
        probability = prediction
        if 1 <= prediction <= 2:
            probability = round(prediction - 1, 2)
        # TODO: fixed if the result > 2 not work correctly
        elif prediction > 2:
            probability = -1
        prediction_data = PredictionData(
            prediction=prediction,
            prediction_round=prediction_round,
            probability=probability,
        )
        return prediction_data
