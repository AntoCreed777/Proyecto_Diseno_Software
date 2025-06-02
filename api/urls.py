from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    UsuarioViewSet,
    ClienteViewSet,
    UsuarioClienteViewSet,
    ConductorViewSet,
    UsuarioConductorViewSet,
    AdminViewSet,
    UsuarioAdminViewSet,
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
router.register('usuarios-clientes', UsuarioClienteViewSet, basename='usuarios-clientes')
router.register('conductores', ConductorViewSet)
router.register('usuarios-conductores', UsuarioConductorViewSet, basename='usuarios-conductores')
router.register('admins', AdminViewSet)
router.register('usuarios-admins', UsuarioAdminViewSet, basename='usuarios-admins')
router.register('vehiculos', VehiculoViewSet)
router.register('rutas', RutaViewSet)
router.register('conductor-posee-rutas', ConductorPoseeRutaViewSet)
router.register('estados-entrega', EstadoEntregaViewSet)
router.register('paquetes', PaqueteViewSet)
router.register('notificaciones', NotificacionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
