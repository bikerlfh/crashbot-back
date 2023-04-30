# Standard Library
from typing import Optional

# Libraries
import numpy as np
from sklearn.linear_model import LinearRegression


def predict(*, data: list[int], length_window: Optional[int] = 10) -> int:
    # Split the list into input and output variables
    X = np.array(  # NOQA
        [data[i : i + length_window] for i in range(len(data) - length_window)]
    )
    y = np.array(data[length_window:])

    # Create and fit the linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict the next number in the sequence
    next_num = model.predict([data[-length_window:]])[0]
    return next_num
