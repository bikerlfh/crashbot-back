"""
this file contains the channels that the
bot will listen to read messages and send to de bots
"""
# Standard Library
import logging
from dataclasses import dataclass

# Internal
from apps.sockets import services as sockets_services
from apps.telegram_bot.constants import CHANNEL_LISTENERS_CONFIG

logger = logging.getLogger(__name__)


@dataclass
class _ChannelListener:
    home_bet_id: int
    chat_id: int
    message: str
    min_multiplier: float
    max_multiplier: float


class ChannelListener:
    CHANNELS = [
        _ChannelListener(**channel) for channel in CHANNEL_LISTENERS_CONFIG
    ]

    @staticmethod
    async def read_message(chat_id: int, message: str):
        channel_ = None
        for channel in ChannelListener.CHANNELS:
            if channel.chat_id == chat_id:
                channel_ = channel
                break
        if channel_ is None or channel_.message.lower() not in message.lower():
            return

        await sockets_services.send_multiplier_bet_to_bots_async(
            home_bet_id=channel_.home_bet_id,
            min_multiplier=channel_.min_multiplier,
            max_multiplier=channel_.max_multiplier,
            chat_id=channel_.chat_id,
        )
        logger.info(
            f"ChannelListener :: " f"multiplier bet sent to bots :: {channel_}"
        )
