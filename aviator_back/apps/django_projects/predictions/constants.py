# Standard Library
from enum import Enum
from os import getenv


class ModelStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


DEFAULT_SEQ_LEN = int(getenv("DEFAULT_SEQ_LEN", 15))
DEFAULT_MODEL_TYPE = getenv("DEFAULT_MODEL_TYPE", "sequential_lstm")
# AVERAGE_PERCENTAGE_ACCEPTABLE
PERCENTAGE_ACCEPTABLE = float(getenv("AVERAGE_PERCENTAGE_ACCEPTABLE", 85))
PERCENTAGE_MODEL_TO_INACTIVE = float(getenv(
    "PERCENTAGE_MODEL_TO_INACTIVE", 60
))
