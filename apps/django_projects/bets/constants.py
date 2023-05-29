# Standard Library
from enum import Enum


class BetStatus(str, Enum):
    PENDING = "pending"
    WON = "won"
    LOST = "lost"


class BetType(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
