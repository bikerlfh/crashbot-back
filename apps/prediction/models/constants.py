# Standard Library
from os import getenv

EPOCHS_SEQUENTIAL_LSTM = int(getenv("EPOCHS_SEQUENTIAL_LSTM", 2000))
EPOCHS_SEQUENTIAL = int(getenv("EPOCHS_SEQUENTIAL", 2000))
