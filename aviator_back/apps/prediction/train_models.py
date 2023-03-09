from decimal import Decimal
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout
from sklearn.model_selection import train_test_split
from apps.prediction import utils
from apps.prediction.constants import MODELS_PATH
from apps.django_projects.core import selectors


def create_sequential_model(
    *,
    home_bet_id: int,
    multipliers: list[Decimal],
    length_window: int,
) -> str:
    nums = utils.transform_multipliers_to_data(multipliers)
    # Split the list into input and output variables
    X = np.array([ # NOQA
        nums[i:i + length_window]
        for i in range(len(nums) - length_window)
    ])
    y = np.array(nums[length_window:])
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2) # NOQA
    # Create and compile the model
    model = Sequential()
    model.add(Dense(64, input_dim=length_window, activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(16, activation='relu'))
    model.add(Dense(1))
    model.compile(loss='mse', optimizer='adam')
    model.fit(X_train, y_train, epochs=1000, batch_size=32)
    # Evaluate the model on the test set
    mse = model.evaluate(X_test, y_test)
    print("Mean squared error on test set:", mse)
    model_path = f"{MODELS_PATH}model_{home_bet_id}_{length_window}_{len(nums)}.h5"
    model.save(model_path)
    return model_path


def create_model_by_home_bet(
    *,
    home_bet_id: int,
    length_window: int
) -> str:
    multipliers = selectors.get_last_multipliers(
        home_bet_id=home_bet_id
    )
    path = create_sequential_model(
        home_bet_id=home_bet_id,
        multipliers=multipliers,
        length_window=length_window
    )
    print(f"model saved at {path}")
    return path
