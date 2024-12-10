import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.meduzzen_backend.settings")

django_asgi_app = get_asgi_application()

# ruff: noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter

from core.notification.websockets.middleware import TokenAuthMiddleware
from core.notification.websockets.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket":TokenAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
})
