# Django
from django.urls import path

# Internal
from apps.sockets.consumers import BotConsumer

websocket_urlpatterns = [
    path("bot/", BotConsumer.as_asgi()),
]
