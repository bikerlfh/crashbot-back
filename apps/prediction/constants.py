# Standard Library
from enum import Enum
from os import getenv

MODELS_PATH = "models_created/"

DATA_EXPORT_PATH = "data/"


class ModelType(str, Enum):
    SEQUENTIAL = "sequential"
    SEQUENTIAL_LSTM = "sequential_lstm"
    GRU = "gru"
    DECISION_TREE_REGRESSOR = "decision_tree_regressor"
    LINEAR_REGRESSOR = "linear_regression"


class Category(int, Enum):
    CATEGORY_1 = 1
    CATEGORY_2 = 2
    CATEGORY_3 = 3


MIN_PROBABILITY_TO_EVALUATE_MODEL = round(
    float(getenv("MIN_PROBABILITY_TO_EVALUATE_MODEL", 0.5)), 2
)

# bucket to store models
S3_BUCKET_MODELS = getenv("S3_BUCKET_MODELS")
