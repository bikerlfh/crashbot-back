# Standard Library
from typing import Optional

# Libraries
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor


def predict(*, data: list[int], length_window: Optional[int] = 10) -> int:
    def _create_features(numbers, _length_window):
        features = []
        for i in range(len(numbers) - _length_window):
            window = numbers[i : i + _length_window]
            features.append(window)
        return np.array(features)

    X = _create_features(data, length_window)  # NOQA
    y = data[length_window:]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)  # NOQA
    modelo = DecisionTreeRegressor()
    modelo.fit(X_train, y_train)
    last_numbers = data[-length_window:]
    next_number = modelo.predict([last_numbers])[0]
    return next_number


def predict_2(*, data: list[int], length_window: Optional[int] = 10) -> int:
    # Split the list into input and output variables
    X = np.array(  # NOQA
        [data[i : i + length_window] for i in range(len(data) - length_window)]
    )
    y = np.array(data[length_window:])

    # Create and fit the decision tree regressor model
    model = DecisionTreeRegressor()
    model.fit(X, y)
    # Predict the next number in the sequence
    next_num = model.predict([data[-length_window:]])[0]
    return next_num
