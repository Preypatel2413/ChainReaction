from django.urls import path
from . import views

urlpatterns = [
    path('Play/<str:room_code>/', views.Play, name='Play'),
    path('Challenge/',views.Challenge, name='Challenge'),
    path('acceptChallenge/<int:index>/', views.acceptChallenge, name='acceptChallenge'),
    path('createChallenge/<int:index>/', views.createChallenge, name='createChallenge'),
    path('randomChallenge/', views.randomChallenge, name='randomChallenge'),
    path('endWait/', views.endWait, name='endWait'),
    path('update_position_/<int:row>/<int:col>/', views.update_position_, name='update_position_'),
    path('clear-data/', views.clear_data, name='clear-data'),
]