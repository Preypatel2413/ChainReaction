from django.urls import path
from . import views

urlpatterns = [
    path('Game/<str:room_code>/', views.Game, name='Game'),
    path('Challenge/',views.Challenge, name='Challenge'),
    path('acceptChallenge/<str:name>/', views.acceptChallenge, name='acceptChallenge'),
    path('createChallenge/<str:name>/', views.createChallenge, name='createChallenge'),
    path('randomChallenge/', views.randomChallenge, name='randomChallenge'),
    path('endWait/<int:index>/', views.endWait, name='endWait'),
    path('update_position_/<int:row>/<int:col>/', views.update_position_, name='update_position_'),
    path('clearGame/<int:win>/<int:p>/', views.clearGame, name='clearGame'),
    path('sendMessage/<int:p>/<str:message>/', views.send_Message, name='send_Message'),
]