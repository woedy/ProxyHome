import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import proxies.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proxyplatform.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            proxies.routing.websocket_urlpatterns
        )
    ),
})