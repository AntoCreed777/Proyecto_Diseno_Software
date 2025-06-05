from django.urls import path
from .views import inicio, paquetes, conductores, registrar_paquete, registrar_cliente, detalles_paquete

urlpatterns = [
    path('inicio/', inicio, name = 'inicio_despachador'),
    path('paquetes/', paquetes, name = 'paquetes_despachador'),
    path('conductores/', conductores, name = 'conductores_despachador'),
    path('registrar-paquete/', registrar_paquete, name='registrar_paquete_despachador'),
    path('registrar-cliente/', registrar_cliente, name='registrar_cliente_despachador'),
    path('detalles-paquete/', detalles_paquete, name='detalles_paquete_despachador'),
]
