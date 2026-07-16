"""ASGI config for KasSekolah project."""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import apps.notifications.routing
import apps.payments.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            apps.notifications.routing.websocket_urlpatterns +
            apps.payments.routing.websocket_urlpatterns
        )
    ),
})