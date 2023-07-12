from django.urls import path
from . import views

urlpatterns = [
    path('Home/', views.Home, name='Home'),
    path('Profile/', views.Profile, name='Profile'),
    path('addfriend/<str:name>', views.add_friend, name='add_friend')
]