import csv
import numpy as np
from typing import Optional
from keras.models import load_model
from decimal import Decimal

from apps.django_projects.core import selectors as core_selectors


def predict(*, data: list[int], length_window: Optional[int] = 10) -> Decimal:
    loaded_model = load_model("apps/prediction/models/model_betplay_10_706.h5")
    next_num = loaded_model.predict(np.array([data[-length_window:]]))[0][0]
    return round(next_num, 2)


def extract_data(*, home_bet_id: int) -> str:
    rows = core_selectors.get_last_multipliers(
        home_bet_id=home_bet_id
    )
    np.savetxt("data.csv",
               rows,
               delimiter=", ",
               fmt='% s')

