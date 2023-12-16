# Standard Library
from typing import Union

# Internal
from apps.telegram_bot.bot import TelegramBot
from apps.telegram_bot.constants import Emoji


def start_telegram_bot():
    """
    use to start telegram bot
    """
    print("staring telegram bot")
    bot = TelegramBot()
    print("telegram bot connected")
    bot.run_until_disconnected()


def send_telegram_message(*, chat_id: int | str, message: str) -> Union[None]:
    bot = TelegramBot()
    bot.send_message(chat_id=chat_id, message=message)


def notify_prediction_to_channel(
    *,
    channel_id: int,
    home_bet_name: str,
    game_name: str,
    last_multiplier: float,
    multiplier_result: float,
    probability: float,
) -> None:
    msg = (
        f"**{Emoji.FIRE.value} {game_name} {Emoji.FIRE.value}**\n"
        f"{Emoji.TROPHY.value} {home_bet_name} \n"
        f"{Emoji.FIRE.value} Entrada: {last_multiplier}\n"
        f"**{Emoji.CHECK_BUTTON.value} Retiro: {multiplier_result}**\n"
        f"{Emoji.PROBABILITY.value} Probabilidad: {probability}%\n\n"
        f"{Emoji.ONLY_ADULTS.value} Juega con responsabilidad {Emoji.ROBOT.value}"
    )
    send_telegram_message(chat_id=channel_id, message=msg)
