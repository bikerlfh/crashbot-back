"""
https://docs.telethon.dev/
https://my.telegram.org/
"""
# Standard Library
import logging
from typing import Union

# Libraries
from telethon import TelegramClient

# Internal
from apps.telegram_bot.constants import (
    TELEGRAM_API_HASH,
    TELEGRAM_API_ID,
    TELEGRAM_CHANNEL_NAME,
    TELEGRAM_PHONE_NUMBER,
)
from apps.telegram_bot.typing import Message
from apps.utils.patterns.singleton import Singleton

logger = logging.getLogger(__name__)


def _validate_config():
    assert isinstance(
        TELEGRAM_PHONE_NUMBER, str
    ), "TELEGRAM_PHONE_NUMBER mush be a str instance"
    assert isinstance(
        TELEGRAM_API_ID, int
    ), "TELEGRAM_API_ID mush be a int instance"
    assert isinstance(
        TELEGRAM_API_HASH, str
    ), "TELEGRAM_API_HASH mush be a str instance"
    assert isinstance(
        TELEGRAM_CHANNEL_NAME, str
    ), "TELEGRAM_CHANNEL_NAME mush be a str instance"


class TelegramConnector(Singleton):
    def __init__(self):
        _validate_config()
        self.client = None
        self.channel = None
        self.channel_name = TELEGRAM_CHANNEL_NAME

    async def connect(self):
        if self.client is not None:
            return
        try:
            self.client = TelegramClient(
                "session", TELEGRAM_API_ID, TELEGRAM_API_HASH
            )
            await self.client.connect()
            if not await self.client.is_user_authorized():
                await self.client.send_code_request(TELEGRAM_PHONE_NUMBER)
                await self.client.sign_in(
                    TELEGRAM_PHONE_NUMBER, input("Enter the code: ")
                )
            # self.channel = await self.
            # client.get_input_entity(TELEGRAM_CHANNEL_ID)
        except Exception as e:
            logger.exception(f"TelegramConnector::connect :: {e}")

    async def disconnect(self):
        await self.client.disconnect()

    async def send_message(self, *, message: Message) -> None:
        try:
            user = self.channel_name
            if message.user:
                user = message.user
            await self.client.send_message(
                user, message.message, parse_mode="html", silent=message.silent
            )
        except Exception as e:
            logger.exception(f"TelegramConnector::send_message :: {e}")
