# Standard Library
from enum import Enum
from os import getenv

BOT_CHANNEL_NAME = getenv("BOT_CHANNEL_NAME", "bots")

APP_VERSION = getenv("APP_VERSION", "1.0.0")


class WSErrorCodes(str, Enum):
    W01 = "W01"
