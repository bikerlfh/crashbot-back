# Standard Library
from enum import Enum
from os import getenv


class ModelStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class BotType(str, Enum):
    AGGRESSIVE = "aggressive"
    TIGHT = "tight"
    LOOSE = "loose"


DEFAULT_SEQ_LEN = int(getenv("DEFAULT_SEQ_LEN", 18))
GENERATE_AUTOMATIC_MODEL_TYPES = getenv(
    "GENERATE_AUTOMATIC_MODEL_TYPES", "sequential,gru,sequential_lstm"
).split(",")
# AVERAGE_PERCENTAGE_ACCEPTABLE
PERCENTAGE_ACCEPTABLE = float(getenv("AVERAGE_PERCENTAGE_ACCEPTABLE", 0.85))
PERCENTAGE_MODEL_TO_INACTIVE = float(
    getenv("PERCENTAGE_MODEL_TO_INACTIVE", 0.59)
)

DIFF_MULTIPLIERS_TO_GENERATE_NEW_MODEL = int(
    getenv("DIFF_MULTIPLIERS_TO_GENERATE_NEW_MODEL", 200)
)

NUMBER_OF_MODELS_TO_PREDICT = int(getenv("NUMBER_OF_MODELS_TO_PREDICT", 2))
