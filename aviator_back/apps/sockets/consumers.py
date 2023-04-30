# Standard Library
import json

# Libraries
from apps.sockets.constants import BOT_CHANNEL_NAME
from channels.generic.websocket import AsyncWebsocketConsumer


class BotConsumer(AsyncWebsocketConsumer):
    GROUP_NAME = BOT_CHANNEL_NAME

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Send message to room group
        await self.channel_layer.group_send(
            self.GROUP_NAME, {"type": "send_message", "message": data}
        )

    # Receive message from room group
    async def send_message(self, event):
        message = event["message"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))
