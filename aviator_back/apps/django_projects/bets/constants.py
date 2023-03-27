# Standard Library
from enum import Enum


class BetStatus(str, Enum):
    PENDING = "pending"
    WON = "won"
    LOST = "lost"
