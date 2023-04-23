# Standard Library
import os
from decimal import Decimal
from typing import Optional, Tuple

# Libraries
import numpy as np
from tensorflow.keras.layers import GRU, Dense
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import f1_score, recall_score, precision_score, confusion_matrix
from sklearn.model_selection import train_test_split
from apps.django_projects.predictions.constants import DEFAULT_SEQ_LEN
from apps.prediction.constants import ModelType
from apps.prediction.models.base import AbstractBaseModel, PredictionData
from apps.prediction import utils


class GRUModel(AbstractBaseModel):
    """
    GRU model class
    not use directly. Use CoreModel instead
    """

    MODEL_EXTENSION = "h5"

    def __init__(
        self,
        *,
        model_type: ModelType,
        seq_len: Optional[int] = DEFAULT_SEQ_LEN,
    ):
        self._epochs = 1000
        super(GRUModel, self).__init__(
            model_type=model_type, seq_len=seq_len
        )
        assert self.model_type == ModelType.GRU, "Invalid model type"

    def _compile_model(self) -> Sequential:
        model = Sequential()
        model.add(GRU(32, input_shape=(self.seq_len, 1)))
        model.add(Dense(self.num_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

    def _split_data_to_train_gru(
        self, data: list[int]
    ) -> Tuple[np.array, np.array]:
        """
        get the list of sequences and the list of next values
        @return: Tuple[train_data, test_data]
        the list of sequences and the list of next values
        """
        x, y = [], []
        for i in range(len(data) - self.seq_len):
            x.append(data[i : i + self.seq_len])
            y.append(data[i + self.seq_len])
        x = np.array(x).reshape(-1, self.seq_len, 1) / float(self.num_classes)
        y = to_categorical(y, num_classes=self.num_classes)
        return x, y

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
        x, y = self._split_data_to_train_gru(data=data)
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=test_size, random_state=42
        )
        model = self._compile_model()
        model.fit(x_train, y_train, epochs=self._epochs, batch_size=32, verbose=2)
        loss, accuracy = model.evaluate(x_test, y_test, verbose=2)
        name, model_path = self._generate_model_path_to_save(
            home_bet_id=home_bet_id
        )
        model.save(model_path)
        print("-------------------------------------------------------------------")
        print(f"--------MODEL: {name} LOSS: {loss} ACCURRACY: {accuracy}----------")
        print("-------------------------------------------------------------------")
        # generate others metrics
        y_pred_prob = model.predict(x_test) # NOQA
        y_pred = np.argmax(y_pred_prob, axis=1) # NOQA
        y_true = np.argmax(y_test, axis=1)
        precision = precision_score(y_true, y_pred, average='weighted')
        recall = recall_score(y_true, y_pred, average='weighted')
        f1 = f1_score(y_true, y_pred, average='weighted')
        # calculate specificity
        cm = confusion_matrix(y_true, y_pred)
        specificity = cm.diagonal() / cm.sum(axis=1)
        metrics = dict(
            loss=loss,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1=f1,
            specificity=specificity.tolist(),
        )
        return name, metrics

    def load_model(self, *, name: str) -> None:
        model_path = self._get_model_path(name=name)
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"file not found'{model_path}'")
        self.model = load_model(model_path)

    def predict(self, *, data: list[int]) -> PredictionData:
        input_sequence = np.array(data[-self.seq_len:]).reshape(1, self.seq_len, 1) / float(self.num_classes)
        probabilities = self.model.predict(input_sequence)[0]
        prediction = int(np.argmax(probabilities))
        prediction_data = PredictionData(
            prediction=prediction,
            prediction_round=prediction,
        )
        return prediction_data
