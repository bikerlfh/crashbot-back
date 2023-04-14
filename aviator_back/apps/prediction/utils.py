# Standard Library
from decimal import Decimal


def transform_multipliers_to_data(multipliers: list[Decimal]):
    data = []
    for num in multipliers:
        if num < 2:
            data.append(1)
            continue
        # elif num < 10:
        #    data.append(2)
        #    continue
        data.append(2)
    return data


def to_float(value: any) -> float:
    return float("{:.2f}".format(value))
