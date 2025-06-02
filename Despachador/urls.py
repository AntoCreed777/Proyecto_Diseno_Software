from django.urls import path
from .views import inicio, paquetes, conductores

urlpatterns = [
    path('inicio/', inicio, name = 'inicio_despachador'),
    path('paquetes/', paquetes, name = 'paquetes_despachador'),
    path('conductores/', conductores, name = 'conductores_despachador'),
]
