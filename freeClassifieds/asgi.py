import os

# 1. Set the Django settings module before any imports that load Django apps
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freeClassifieds.settings')

# 2. Perform Django setup to initialize app registry
import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from main.middleware import JwtAuthMiddleware
import main.routing

# 3. Instantiate Django ASGI app and route protocols
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddleware(
        URLRouter(main.routing.websocket_urlpatterns)
    ),
})
