

# --------- app/routing.py ----------------

from django.urls import  path
from . import consumer

websocket_urlpatterns = [
    path('ws/ac/', consumer.UpdatedDataConsumer.as_asgi())
]