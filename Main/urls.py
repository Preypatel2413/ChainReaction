from django.urls import path
from . import views

urlpatterns = [
    path('Main/', views.Main, name='Main'),
    path('update_position/<int:row>/<int:col>/', views.update_position, name='update_position'),
    path('clear-data/', views.clear_data, name='clear-data'),
]