from rest_framework import routers
from django.urls import path, include
from .views import *

router = routers.DefaultRouter()
router.register(r'clientes', ClienteListView)
router.register(r'conductores', ConductorListView)
router.register(r'administradores', AdminListView)
router.register(r'vehiculos', VehiculoListView)
router.register(r'rutas', RutaListView)
router.register(r'paquetes', PaqueteListView)
router.register(r'notificaciones', NotificacionListView)
router.register(r'entregas', EntregaListView)

urlpatterns = [
    path('', include(router.urls)),
]