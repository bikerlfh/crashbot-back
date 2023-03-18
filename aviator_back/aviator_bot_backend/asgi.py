"""
ASGI config for aviator_bot_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

# Standard Library
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
# Django
from django.core.asgi import get_asgi_application
from apps.sockets import routing as sockets_rounting

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aviator_bot_backend.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(sockets_rounting.websocket_urlpatterns))
    ),
})

