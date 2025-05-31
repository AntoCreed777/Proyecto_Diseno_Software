from django.urls import path
from .views import inicio, paquetes, conductores

urlpatterns = [
    path('inicio/', inicio, name = 'inicio'),
    path('paquetes/', paquetes, name = 'paquetes'),
    path('conductores/', conductores, name = 'conductores'),
]
