# Standard Library
import uuid
from typing import Optional, Tuple

# Libraries
import numpy as np
from keras.layers import LSTM, Dense, Dropout
from keras.models import Sequential
from sklearn.model_selection import train_test_split

# Internal
from apps.prediction.constants import MODELS_PATH


def create_sequential_model(
    *,
    home_bet_id: int,
    data: list[int],
    seq_len: int,
    test_size: Optional[float] = 0.2,
) -> Tuple[str, float]:
    """
    create a sequential model and return the name and evaluation result
    """
    # Split the list into input and output variables
    X = np.array(  # NOQA
        [data[i: i + seq_len] for i in range(len(data) - seq_len)]
    )
    y = np.array(data[seq_len:])
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(  # NOQA
        X, y, test_size=test_size
    )
    # Create and compile the model
    model = Sequential()
    model.add(Dense(64, input_dim=seq_len, activation="relu"))
    model.add(Dense(32, activation="relu"))
    model.add(Dropout(0.2))
    model.add(Dense(16, activation="relu"))
    model.add(Dense(1))
    model.compile(loss="mse", optimizer="adam")
    model.fit(X_train, y_train, epochs=3000, batch_size=32)
    # Evaluate the model on the test set
    mse = model.evaluate(X_test, y_test)
    # print("Mean squared error on test set:", mse)
    name = f"{home_bet_id}_{uuid.uuid4()}.h5"
    model_path = f"{MODELS_PATH}{name}"
    model.save(model_path)
    print("---------------------------------------------")
    print(f"--------MODEL: {name} ERROR: {mse}----------")
    print("---------------------------------------------")
    return name, mse


def create_sequential_lstm_model(
    *,
    home_bet_id: int,
    data: list[int],
    seq_len: int,
) -> Tuple[str, float]:
    X = np.array(  # NOQA
        [data[i: i + seq_len] for i in range(len(data) - seq_len)]
    )
    y = np.array(data[seq_len:])
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42) # NOQA
    # Create and compile the model
    model = Sequential()
    model.add(LSTM(units=32, input_shape=(seq_len, 1)))
    model.add(Dense(units=1))
    model.compile(loss='mse', optimizer='adam')
    model.fit(X_train, y_train, batch_size=32, epochs=4000)

    # Evaluate the model on the test set
    mse = model.evaluate(X_test, y_test)
    name = f"{home_bet_id}_{uuid.uuid4()}.h5"
    model_path = f"{MODELS_PATH}{name}"
    model.save(model_path)
    print("---------------------------------------------")
    print(f"--------MODEL: {name} ERROR: {mse}----------")
    print("---------------------------------------------")
    return name, mse
