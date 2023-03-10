# Standard Library
from enum import Enum

MODELS_PATH = "apps/prediction/models/"

DATA_EXPORT_PATH = "data/"


class ModelType(str, Enum):
    SEQUENTIAL = "sequential"
    DECISION_TREE_REGRESSOR = "decision_tree_regressor"
    LINEAR_REGRESSOR = "linear_regression"


class Category(int, Enum):
    CATEGORY_1 = 1
    CATEGORY_2 = 2
    CATEGORY_3 = 3
