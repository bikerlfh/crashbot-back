# Standard Library
from decimal import Decimal
from typing import Optional, Tuple

# Libraries
import numpy as np
from keras.layers import Dense, Dropout
from keras.models import Sequential
from sklearn.model_selection import train_test_split

# Internal
from apps.prediction import utils
from apps.prediction.constants import MODELS_PATH


def create_sequential_model(
    *,
    home_bet_id: int,
    multipliers: list[Decimal],
    length_window: int,
    test_size: Optional[Decimal] = Decimal(0.2),
) -> Tuple[str, Decimal]:
    """
    create a sequential model and return the path and evaluation result
    """
    nums = utils.transform_multipliers_to_data(multipliers)
    # Split the list into input and output variables
    X = np.array( # NOQA
        [
            nums[i: i + length_window]
            for i in range(len(nums) - length_window)
        ]
    )
    y = np.array(nums[length_window:])
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(  # NOQA
        X, y, test_size=test_size
    )
    # Create and compile the model
    model = Sequential()
    model.add(Dense(64, input_dim=length_window, activation="relu"))
    model.add(Dense(32, activation="relu"))
    model.add(Dropout(0.2))
    model.add(Dense(16, activation="relu"))
    model.add(Dense(1))
    model.compile(loss="mse", optimizer="adam")
    model.fit(X_train, y_train, epochs=1000, batch_size=32)
    # Evaluate the model on the test set
    mse = model.evaluate(X_test, y_test)
    # print("Mean squared error on test set:", mse)
    model_path = (
        f"{MODELS_PATH}model_" f"{home_bet_id}_{length_window}_{len(nums)}.h5"
    )
    model.save(model_path)
    return model_path, mse
