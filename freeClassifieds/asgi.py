import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freeClassifieds.settings')
django.setup()

from main.middleware import JwtAuthMiddleware
from main import routing

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': JwtAuthMiddleware(
        URLRouter(routing.websocket_urlpatterns)
    ),
})
