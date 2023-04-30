"""
https://docs.telethon.dev/
https://my.telegram.org/

bot = TelegramBot(api_id, api_hash, phone_number)
# wait for the event handler
bot.run_until_disconnected()
"""
# Standard Library
import logging
from typing import Optional

# Libraries
from apps.telegram_bot.channel_listeners import ChannelListener
from apps.telegram_bot.constants import (
    TELEGRAM_API_HASH,
    TELEGRAM_API_ID,
    TELEGRAM_PHONE_NUMBER,
)
from apps.utils.patterns.singleton import Singleton
from telethon.sync import TelegramClient, events
from telethon.tl.types import PeerChannel, PeerUser

logger = logging.getLogger(__name__)


class TelegramBot(Singleton):
    def __init__(self):
        assert isinstance(
            TELEGRAM_PHONE_NUMBER, str
        ), "TELEGRAM_PHONE_NUMBER mush be a str instance"
        assert isinstance(
            TELEGRAM_API_ID, int
        ), "TELEGRAM_API_ID mush be a int instance"
        assert isinstance(
            TELEGRAM_API_HASH, str
        ), "TELEGRAM_API_HASH mush be a str instance"
        self.client = None
        self.connect()

    def connect(self):
        if self.client is not None:
            return
        try:
            self.client = TelegramClient("session", TELEGRAM_API_ID, TELEGRAM_API_HASH)
            self.client.connect()
            if not self.client.is_user_authorized():
                self.client.send_code_request(TELEGRAM_PHONE_NUMBER)
                self.client.sign_in(TELEGRAM_PHONE_NUMBER, input("Enter the code: "))
            self.client.add_event_handler(self.handle_message, events.NewMessage())
        except Exception as e:
            logger.exception(f"TelegramBot::connect :: {e}")

    def disconnect(self):
        self.client.disconnect()

    def send_message(
        self,
        *,
        chat_id: int | str,
        message: str,
        parse_mode: Optional[str] = (),
        silent: Optional[bool] = False,
        **kwargs,
    ) -> None:
        try:
            self.client.send_message(
                chat_id,
                message,
                parse_mode=parse_mode,
                silent=silent,
                **kwargs,
            )
        except Exception as e:
            logger.exception(f"TelegramBot :: send_message :: {e}")

    async def handle_message(self, event):  # NOQA
        message = event.message
        peer = message.peer_id
        chat_id = None
        if isinstance(peer, PeerChannel):
            chat_id = peer.channel_id
        elif isinstance(peer, PeerUser):
            chat_id = peer.user_id
        text = message.message
        print(f"handle_message: {text}, chat_id: {chat_id}")
        await ChannelListener.read_message(chat_id, text)

    def run_until_disconnected(self):
        self.client.run_until_disconnected()
