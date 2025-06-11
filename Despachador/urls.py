from django.urls import path
from .views import inicio, paquetes, conductores, registrar_paquete, registrar_cliente, asignar_conductor, cambiar_estado_paquete
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('inicio/', inicio, name = 'inicio_despachador'),
    path('paquetes/', paquetes, name = 'paquetes_despachador'),
    path('conductores/', conductores, name = 'conductores_despachador'),
    path('registrar-paquete/', registrar_paquete, name='registrar_paquete_despachador'),
    path('registrar-cliente/', registrar_cliente, name='registrar_cliente_despachador'),
    path('asignar-conductor/', asignar_conductor, name='asignar_conductor_despachador'),
    path('cambiar-estado/', cambiar_estado_paquete, name='cambiar_estado_paquete'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
