from django.urls import re_path, path

from apps.sockets.consumers import BotConsumer


websocket_urlpatterns = [
    path("bot/", BotConsumer.as_asgi()),
    
]