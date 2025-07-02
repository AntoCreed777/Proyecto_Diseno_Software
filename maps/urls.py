from django.urls import path
from . import views


app_name = 'maps'  # Define el namespace

urlpatterns = [
    path('', views.map, name='map'),
    path('paquete/<int:paquete_id>/', views.map_paquete, name='map_paquete'),
]
