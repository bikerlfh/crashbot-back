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
from apps.prediction.constants import ModelType
from apps.prediction.models.base import AbstractBaseModel
from apps.prediction import utils


class SequentialModel(AbstractBaseModel):
    """
    sequential model class
    not use directly. Use CoreModel instead
    """

    MODEL_EXTENSION = "h5"

    def __init__(
        self,
        *,
        model_type: ModelType,
        seq_len: Optional[int] = DEFAULT_SEQ_LEN,
    ):
        self._epochs = 3000
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
            case ModelType.SEQUENTIAL_LSTM:
                model.add(LSTM(units=32, input_shape=(self.seq_len, 1)))
                model.add(Dense(units=1))
                self._epochs = 4000
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
    ) -> Tuple[str, float]:
        data = utils.transform_multipliers_to_data(multipliers)
        self._epochs = epochs or self._epochs
        X, y = self._split_data_to_train(data=data)  # NOQA
        X_train, X_test, y_train, y_test = train_test_split(  # NOQA
            X, y, test_size=test_size, random_state=42
        )
        model = self._compile_model()
        model.fit(X_train, y_train, epochs=self._epochs, batch_size=32)
        mse = model.evaluate(X_test, y_test)
        name, model_path = self._generate_model_path_to_save(
            home_bet_id=home_bet_id
        )
        model.save(model_path)
        print("---------------------------------------------")
        print(f"--------MODEL: {name} ERROR: {mse}----------")
        print("---------------------------------------------")
        return name, mse

    def load_model(self, *, name: str) -> None:
        model_path = self._get_model_path(name=name)
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"file not found'{model_path}'")
        self.model = load_model(model_path)

    def predict(self, *, data: list[int]) -> Decimal:
        next_num = self.model.predict(np.array([data[-self.seq_len :]]))[0][0]
        return round(next_num, 2)
