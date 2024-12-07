
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from kafka.routing import websocket_urlpatterns  # Import the websocket URL patterns for routing
from channels.auth import AuthMiddlewareStack  # Middleware to handle user authentication for WebSockets

# Set the default settings module for the Django project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangochannels.settings')

# Define the ASGI application protocol router
application = ProtocolTypeRouter({
    # HTTP protocol is handled by Django's ASGI application
    "http": get_asgi_application(),
    
    # WebSocket protocol is handled by Channels with user authentication
    "websocket": AuthMiddlewareStack(  # Wrap WebSocket requests with authentication middleware
        URLRouter(  # Route WebSocket connections based on URL patterns
            websocket_urlpatterns  # The URL patterns for WebSocket connections defined in app.routing
        )
    ),
})