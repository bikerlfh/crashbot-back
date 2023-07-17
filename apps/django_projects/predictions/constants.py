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


class ConditionON(str, Enum):
    # values are float
    EVERY_WIN = "every_wins"
    EVERY_LOSS = "every_loss"
    STREAK_WINS = "streak_wins"
    STREAK_LOSSES = "streak_losses"
    # values are percentage
    PROFIT_GREATER_THAN = "profit_greater_than"
    PROFIT_LESS_THAN = "profit_less_than"


class ConditionAction(str, Enum):
    # values are percentage
    INCREASE_BET_AMOUNT = "increase_bet_amount"
    DECREASE_BET_AMOUNT = "decrease_bet_amount"
    RESET_BET_AMOUNT = "reset_bet_amount"
    # values are float
    UPDATE_MULTIPLIER = "update_multiplier"
    RESET_MULTIPLIER = "reset_multiplier"
    # values are boolean
    IGNORE_MODEL = "ignore_model"


DEFAULT_SEQ_LEN = int(getenv("DEFAULT_SEQ_LEN", 18))
GENERATE_AUTOMATIC_MODEL_TYPES = getenv(
    "GENERATE_AUTOMATIC_MODEL_TYPES", "sequential,gru,sequential_lstm"
).split(",")
# AVERAGE_PERCENTAGE_ACCEPTABLE
PERCENTAGE_ACCEPTABLE = float(getenv("AVERAGE_PERCENTAGE_ACCEPTABLE", 0.85))
PERCENTAGE_MODEL_TO_INACTIVE = float(getenv("PERCENTAGE_MODEL_TO_INACTIVE", 0.59))

DIFF_MULTIPLIERS_TO_GENERATE_NEW_MODEL = int(
    getenv("DIFF_MULTIPLIERS_TO_GENERATE_NEW_MODEL", 50)
)

NUMBER_OF_MODELS_TO_PREDICT = int(getenv("NUMBER_OF_MODELS_TO_PREDICT", 2))

NUMBER_OF_MULTIPLIERS_TO_EVALUATE_MODEL = int(
    getenv("NUMBER_OF_MULTIPLIERS_TO_EVALUATE_MODEL", 200)
)


MIN_MULTIPLIERS_TO_GENERATE_MODEL = int(
    getenv("MIN_MULTIPLIERS_TO_GENERATE_MODEL", 200)
)
