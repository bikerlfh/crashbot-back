# Standard Library
import json
import logging
import uuid
from typing import Optional

# Libraries
from channels.generic.websocket import AsyncWebsocketConsumer

# Internal
from apps.sockets.constants import BOT_CHANNEL_NAME
from apps.sockets.models import SocketMessage, UserConnection

logger = logging.getLogger(__name__)


class BotConsumer(AsyncWebsocketConsumer):
    """
    BOTConsumer that manages which user is allowed to
    send multipliers to the backend to save the multipliers.
    (Users are not authenticated)

    NOTE: you can add other functions to send to the bot.
    The message must have the following structure:
        dict(
            func: name of function to process the messages,
            kwargs: dict of arguments to send to the function
        )
    """

    GROUP_NAME = BOT_CHANNEL_NAME
    user_connections: dict[int | str, dict[str, UserConnection]] = {
        "initial": {}
    }

    def _find_user(self, *, unique_id: str) -> UserConnection | None:
        for key, values in self.user_connections.items():
            if unique_id in list(values.keys()):
                return self.user_connections[key][unique_id]

    def _find_user_allowed_to_save_multiplier(
        self, *, home_bet_id: int
    ) -> UserConnection | None:
        if home_bet_id not in self.user_connections:
            return
        home_bet_users = self.user_connections[home_bet_id]
        for _, user in home_bet_users.items():
            if user.home_bet_id != home_bet_id:
                continue
            allowed_to_save = user.allowed_to_save
            if allowed_to_save:
                return user

    async def _notify_allowed_to_save(
        self, *, home_bet_id: int, unique_id: str
    ) -> None:
        user = self.user_connections[home_bet_id][unique_id]
        channel_name = user.channel_name
        self.user_connections[home_bet_id][unique_id].allowed_to_save = True
        await self.channel_layer.send(
            channel_name,
            {
                "type": "send_message",
                "data": dict(
                    func="notify_allowed_to_save", data=dict(allowed=True)
                ),
            },
        )

    async def _user_joined(self, *, unique_id: str, channel_name: str):
        user = UserConnection(channel_name=channel_name, allowed_to_save=False)
        self.user_connections["initial"][unique_id] = user

    async def _user_joined_to_home_bet(
        self, *, home_bet_id: int, unique_id: str
    ):
        user_allowed = self._find_user_allowed_to_save_multiplier(
            home_bet_id=home_bet_id
        )
        allowed_ = user_allowed is None
        user = self.user_connections["initial"][unique_id]
        user.home_bet_id = home_bet_id
        if home_bet_id not in self.user_connections:
            self.user_connections[home_bet_id] = {}
        self.user_connections[home_bet_id][unique_id] = user
        self.user_connections["initial"].pop(unique_id)
        if allowed_:
            await self._notify_allowed_to_save(
                home_bet_id=home_bet_id, unique_id=unique_id
            )

    async def _user_left(
        self, *, unique_id: str, home_bet_id: Optional[int] = None
    ):
        if not home_bet_id:
            self.user_connections["initial"].pop(unique_id)
            return
        user = self.user_connections[home_bet_id][unique_id]
        self.user_connections[home_bet_id].pop(unique_id)
        if not user.allowed_to_save:
            return
        if not self.user_connections:
            return
        # next user
        home_bet_users = list(self.user_connections[home_bet_id].keys())
        if not home_bet_users:
            return
        unique_id = home_bet_users[0]
        await self._notify_allowed_to_save(
            home_bet_id=home_bet_id, unique_id=unique_id
        )

    async def connect(self):
        unique_id = str(uuid.uuid4())
        self.room_group_name = self.GROUP_NAME
        self.scope["unique_id"] = unique_id
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()
        await self._user_joined(
            unique_id=unique_id, channel_name=self.channel_name
        )
        # remove this
        client_host = self.scope.get('client')
        await self.channel_layer.send(
            self.channel_name,
            {
                "type": "send_message",
                "data": dict(
                    client_host=client_host
                ),
            },
        )

    async def disconnect(self, close_code):
        home_bet_id = self.scope.get("home_bet_id", None)
        unique_id = self.scope["unique_id"]
        await self._user_left(home_bet_id=home_bet_id, unique_id=unique_id)
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
        message = SocketMessage(**json.loads(text_data))
        data = message.data
        unique_id = self.scope["unique_id"]
        user = self._find_user(unique_id=unique_id)
        await self.channel_layer.send(
            user.channel_name, {"type": message.func, "data": data}
        )

    # Receive message from room group
    async def send_message(self, event: dict[str, any]):
        message = event["data"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))

    async def set_home_bet(self, event: dict[str, any]):
        """
        set user to home_bet_id
        """
        data = event["data"]
        home_bet_id = data.get("home_bet_id", None)
        if not home_bet_id:
            return
        self.scope["home_bet_id"] = home_bet_id
        unique_id = self.scope["unique_id"]
        await self._user_joined_to_home_bet(
            home_bet_id=home_bet_id, unique_id=unique_id
        )
