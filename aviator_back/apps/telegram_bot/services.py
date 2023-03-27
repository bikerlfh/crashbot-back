# Standard Library
from typing import Union

# Internal
from apps.telegram_bot.bot import TelegramBot


def start_telegram_bot():
    """
    use to start telegram bot
    """
    print("staring telegram bot")
    bot = TelegramBot()
    print("telegram bot connected")
    bot.run_until_disconnected()


def send_telegram_message(*, chat_id: int, message: str) -> Union[None]:
    bot = TelegramBot()
    bot.send_message(chat_id=chat_id, message=message)
