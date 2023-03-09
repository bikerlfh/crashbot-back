import numpy as np
from datetime import datetime
from typing import Optional
from apps.django_projects.predictions.predict import decision_tree_regressor, linear_regression
from apps.django_projects.predictions.predict.sequential import SequentialPrediction
from apps.django_projects.core import selectors as core_selectors
from decimal import Decimal


def _transform_multipliers_to_categories(
    *,
    multipliers: list[Decimal]
) -> list[int]:
    data = []
    for num in multipliers:
        if num < Decimal(2):
            data.append(1)
            continue
        elif num < Decimal(10):
            data.append(2)
            continue
        data.append(3)
    return data


def predict(
    *,
    home_bet_id: int,
    multipliers: Optional[list[Decimal]] = None,
    length_window: Optional[int] = 10
) -> dict[str, Decimal]:
    if not multipliers:
        multipliers = core_selectors.get_last_multipliers(
            home_bet_id=home_bet_id,
            count=100
        )
    data = _transform_multipliers_to_categories(multipliers=multipliers)
    sequential = SequentialPrediction(
        model_path='apps/prediction/models/model_betplay_10_706.h5'
    )
    sequential_2 = SequentialPrediction(
        model_path='apps/prediction/models/model_betplay_15_706.h5'
    )
    """
    decision_tree = decision_tree_regressor.predict(
        data=data,
        length_window=length_window
    )
    decision_tree_2 = decision_tree_regressor.predict_2(
        data=data,
        length_window=length_window
    )
    linear = linear_regression.predict(
        data=data,
        length_window=length_window
    )
    """
    sequential_ = sequential.predict(
        data=data,
    )
    sequential_2_ = sequential_2.predict(
        data=data
    )
    return_data = dict(
        # decision_tree=round(decision_tree, 2),
        # decision_tree_2=round(decision_tree_2, 2),
        # linear_regression=round(linear, 2),
        sequential=sequential_,
        sequential_2=sequential_2_
    )
    return return_data


def get_average_of_predictions(
    *,
    home_bet_id: int
) -> dict[any, any]:
    now = datetime.now().date()
    multipliers = core_selectors.get_last_multipliers(
        home_bet_id=home_bet_id,
        #filter_=dict(
        #    multiplier_dt__date__lt=now
        #)
    )
    data = _transform_multipliers_to_categories(multipliers=multipliers)
    sequential_340 = SequentialPrediction(
        model_path='apps/prediction/models/model_betplay_10_340.h5'
    )
    sequential_706 = SequentialPrediction(
        model_path='apps/prediction/models/model_betplay_10_706.h5'
    )
    sequential_15_706 = SequentialPrediction(
        model_path='apps/prediction/models/model_betplay_15_706.h5'
    )
    sequential_15_1052 = SequentialPrediction(
        model_path='apps/prediction/models/model_2_15_1052.h5'
    )
    print("----------- average_info_340----------------")
    #average_info_340 = sequential_340.evaluate(data=data)
    print("----------- average_info_706----------------")
    average_info_706 = sequential_706.evaluate(data=data)
    print("----------- average_info_15_706----------------")
    average_info_15_706 = sequential_15_706.evaluate(data=data)
    print("----------- sequential_15_1052----------------")
    average_info_15_1052 = sequential_15_1052.evaluate(data=data)
    average_info = dict(
        #sequential_340=average_info_340,
        sequential_706=average_info_706,
        sequential_15_706=average_info_15_706,
        sequential_15_1052=average_info_15_1052,
    )
    return average_info
