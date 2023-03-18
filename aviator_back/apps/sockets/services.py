import channels.layers
from asgiref.sync import async_to_sync
from apps.sockets.constants import BOT_CHANNEL_NAME


def send_message_to_bots(message: dict) -> None:
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        BOT_CHANNEL_NAME, {'type': 'send_message', "message": message}
    )
