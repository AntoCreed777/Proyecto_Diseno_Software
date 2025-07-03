from django.urls import path
from .views import inicio, paquetes, conductores, registrar_paquete, registrar_cliente, asignar_conductor, cambiar_estado_paquete,cambiar_direccion
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('inicio/', inicio, name = 'inicio_administrador'),
    path('paquetes/', paquetes, name = 'paquetes_administrador'),
    path('conductores/', conductores, name = 'conductores_administrador'),
    path('registrar-paquete/', registrar_paquete, name='registrar_paquete_administrador'),
    path('registrar-cliente/', registrar_cliente, name='registrar_cliente_administrador'),
    path('asignar-conductor/', asignar_conductor, name='asignar_conductor_administrador'),
    path('cambiar-estado/', cambiar_estado_paquete, name='cambiar_estado_paquete_administrador'),
    path('cambiar-direccion/', cambiar_direccion, name="cambiar_direccion_paquete"),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
