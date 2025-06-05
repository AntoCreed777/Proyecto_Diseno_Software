from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    UsuarioViewSet,
    ClienteViewSet,
    ConductorViewSet,
    DespachadorViewSet,
    AdminViewSet,
    VehiculoViewSet,
    RutaViewSet,
    ConductorPoseeRutaViewSet,
    EstadoEntregaViewSet,
    PaqueteViewSet,
    NotificacionViewSet
)

router = DefaultRouter()
router.register('usuarios', UsuarioViewSet)
router.register('clientes', ClienteViewSet)
router.register('conductores', ConductorViewSet)
router.register('despachador', DespachadorViewSet)
router.register('admins', AdminViewSet)
router.register('vehiculos', VehiculoViewSet)
router.register('rutas', RutaViewSet)
router.register('conductor-posee-rutas', ConductorPoseeRutaViewSet)
router.register('estados-entrega', EstadoEntregaViewSet)
router.register('paquetes', PaqueteViewSet)
router.register('notificaciones', NotificacionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
