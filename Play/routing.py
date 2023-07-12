# from .consumers import GameRoom
# from django.urls import path

# websocket_urlpatterns=[
#     path('ws/game/<room_code>/',GameRoom.as_asgi(),name="game"),
# ]


################################################
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from . import consumers

# URLs that handle the WebSocket connection are placed here.
websocket_urlpatterns=[
                    path("ws/Play/<room_code>", consumers.GameRoom.as_asgi(), name = "Play"),
                ]

# application = ProtocolTypeRouter( 
#     {
#         "websocket": AuthMiddlewareStack(
#             URLRouter(
#                websocket_urlpatterns
#             )
#         ),
#     }
# )