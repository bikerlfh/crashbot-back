# Django
from django.urls import path

# Internal
from apps.sockets.consumers import BotConsumer

websocket_urlpatterns = [
    # path("bot/<int:home_bet>/", BotConsumer.as_asgi()),
    path("ws/bot/", BotConsumer.as_asgi()),
]
