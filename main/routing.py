from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # your existing, preferred route:
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
    # fallback if the client connects without the 'ws/' prefix:
    re_path(r'chat/$',     consumers.ChatConsumer.as_asgi()),

    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'notifications/$',     consumers.NotificationConsumer.as_asgi()),
]
