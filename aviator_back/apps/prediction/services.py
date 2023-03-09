import numpy as np
from apps.django_projects.core import selectors as core_selectors
from apps.prediction import utils
from apps.prediction.constants import DATA_EXPORT_PATH


def extract_multipliers_to_csv(*, home_bet_id: int):
    multipliers = core_selectors.get_last_multipliers(
        home_bet_id=home_bet_id
    )
    data = utils.transform_multipliers_to_data(multipliers)
    np.savetxt(
        f"{DATA_EXPORT_PATH}data_{home_bet_id}_{len(data)}.csv",
        data,
        delimiter=", ",
        fmt='% s'
    )
