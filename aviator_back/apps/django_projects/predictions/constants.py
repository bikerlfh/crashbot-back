# Standard Library
from enum import Enum
from os import getenv


class ModelStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class StrategyType(str, Enum):
    AGRESSIVE = "agressive"
    TIGHT = "tight"
    LOOSE = "losse"
    


DEFAULT_SEQ_LEN = int(getenv("DEFAULT_SEQ_LEN", 18))
GENERATE_AUTOMATIC_MODEL_TYPES = getenv(
    "GENERATE_AUTOMATIC_MODEL_TYPES", "sequential,sequential_lstm"
).split(",")
# AVERAGE_PERCENTAGE_ACCEPTABLE
PERCENTAGE_ACCEPTABLE = float(getenv("AVERAGE_PERCENTAGE_ACCEPTABLE", 85))
PERCENTAGE_MODEL_TO_INACTIVE = float(
    getenv("PERCENTAGE_MODEL_TO_INACTIVE", 60)
)
