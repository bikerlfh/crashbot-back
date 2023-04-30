# Standard Library
from typing import Optional

# Libraries
import channels.layers
from apps.sockets.constants import BOT_CHANNEL_NAME
from asgiref.sync import async_to_sync


def send_message_to_bots(message: dict) -> None:
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        BOT_CHANNEL_NAME, {"type": "send_message", "message": message}
    )


async def send_message_to_bots_async(message: dict) -> None:
    channel_layer = channels.layers.get_channel_layer()
    await channel_layer.group_send(
        BOT_CHANNEL_NAME, {"type": "send_message", "message": message}
    )


def send_multiplier_bet_to_bots(
    *,
    home_bet_id: int,
    min_multiplier: float,
    max_multiplier: float,
    chat_id: Optional[int] = None,
    others: Optional[dict] = None,
) -> None:
    send_message_to_bots(
        dict(
            home_bet_id=home_bet_id,
            min_multiplier=min_multiplier,
            max_multiplier=max_multiplier,
            chat_id=chat_id,
            others=others,
        )
    )


async def send_multiplier_bet_to_bots_async(
    *,
    home_bet_id: int,
    min_multiplier: float,
    max_multiplier: float,
    chat_id: Optional[int] = None,
    others: Optional[dict] = None,
) -> None:
    await send_message_to_bots_async(
        dict(
            home_bet_id=home_bet_id,
            min_multiplier=min_multiplier,
            max_multiplier=max_multiplier,
            chat_id=chat_id,
            others=others,
        )
    )
