from typing import Optional
from apps.django_projects.predictions.predict import decision_tree_regressor, linear_regression, sequential
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
) -> dict[str, int]:
    if not multipliers:
        multipliers = core_selectors.get_last_multipliers(
            home_bet_id=home_bet_id
        )
    data = _transform_multipliers_to_categories(multipliers=multipliers)
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
    sequential_ = sequential.predict(
        data=data,
        # length_window=length_window
    )
    return_data = dict(
        decision_tree=round(decision_tree, 2),
        decision_tree_2=round(decision_tree_2, 2),
        linear_regression=round(linear, 2),
        sequential=sequential_
    )
    return return_data
