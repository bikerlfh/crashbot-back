# Standard Library
from enum import Enum
from os import getenv

TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_PHONE_NUMBER = getenv("TELEGRAM_PHONE_NUMBER")
TELEGRAM_API_ID = int(getenv("TELEGRAM_API_ID", 0))
TELEGRAM_API_HASH = getenv("TELEGRAM_API_HASH")

# CHANNELS LISTENERS CONFIG
AVIATOR_COLOMBIA_CHAT_ID = int(getenv("AVIATOR_COLOMBIA_CHAT_ID", 1864888051))
AVIATOR_COLOMBIA_MESSAGE_TO_SEARCH = getenv(
    "AVIATOR_COLOMBIA_MESSAGE_TO_SEARCH",
    "Vamos a tomar la ronda ahora mismo. El retiro Automatico en 1.95",
)
CHANNEL_LISTENERS_CONFIG = [
    dict(
        home_bet_id=3,
        chat_id=AVIATOR_COLOMBIA_CHAT_ID,
        message=AVIATOR_COLOMBIA_MESSAGE_TO_SEARCH,
        min_multiplier=1.95,
        max_multiplier=3,
    ),
    dict(  # TEST USER PAO
        home_bet_id=1,
        chat_id=5759433798,
        message="hola",
        min_multiplier=2,
        max_multiplier=2.5,
    ),
]


class Emoji(Enum):
    CHECK_BUTTON = "\u2705"
    CROSS_MARK = "\u274C"
    MONEY_FACE = "\U0001F911"
    MONEY_BAG = "\U0001F4B0"
    MONEY_WINGS = "\U0001F4B8"
    DOLLAR = "\U0001F4B5"
    WATCH = "\u231A"
    TROPHY = "\U0001F3C6"
    PING_PONG = "\U0001F3D3"
    CLOVER = "\U0001F340"
    FIRE = "\U0001F525"
    ONLY_ADULTS = "\U0001F51E"
    ROBOT = "\U0001F916"
    MEDAL = "\U0001F3C5"
    MEDAL_2 = "\U0001F396"
    MEDAL_STAR = "\U0001F947"
    ROCKETS = "\U0001F680"
    PROBABILITY = "\U0001F4AF"
