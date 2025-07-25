import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freeClassifieds.settings')


import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from main.middleware import JwtAuthMiddleware
import main.routing


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddleware(
        URLRouter(main.routing.websocket_urlpatterns)
    ),
})
