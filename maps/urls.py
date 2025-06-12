from django.urls import path
from . import views


app_name = 'maps'  # Define el namespace

urlpatterns = [
    path('', views.map, name='map'),
]
