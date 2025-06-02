from rest_framework import viewsets, permissions
from .models import (
    Usuario, Cliente, Conductor, Admin, Vehiculo, Ruta,
    ConductorPoseeRuta, EstadoEntrega, Paquete, Notificacion
)
from .serializers import (
    UsuarioSerializer, ClienteSerializer, UsuarioClienteSerializer,
    ConductorSerializer, UsuarioConductorSerializer, AdminSerializer,
    UsuarioAdminSerializer, VehiculoSerializer, RutaSerializer,
    ConductorPoseeRutaSerializer, EstadoEntregaSerializer,
    PaqueteSerializer, NotificacionSerializer
)

# Usuario ViewSet
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

# Cliente ViewSet
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

# Usuario-Cliente ViewSet
class UsuarioClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = UsuarioClienteSerializer

# Conductor ViewSet
class ConductorViewSet(viewsets.ModelViewSet):
    queryset = Conductor.objects.all()
    serializer_class = ConductorSerializer

# Usuario-Conductor ViewSet
class UsuarioConductorViewSet(viewsets.ModelViewSet):
    queryset = Conductor.objects.all()
    serializer_class = UsuarioConductorSerializer

# Admin ViewSet
class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

# Usuario-Admin ViewSet
class UsuarioAdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = UsuarioAdminSerializer

# Vehículo ViewSet
class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer

# Ruta ViewSet
class RutaViewSet(viewsets.ModelViewSet):
    queryset = Ruta.objects.all()
    serializer_class = RutaSerializer

# ConductorPoseeRuta ViewSet
class ConductorPoseeRutaViewSet(viewsets.ModelViewSet):
    queryset = ConductorPoseeRuta.objects.all()
    serializer_class = ConductorPoseeRutaSerializer

# EstadoEntrega ViewSet
class EstadoEntregaViewSet(viewsets.ModelViewSet):
    queryset = EstadoEntrega.objects.all()
    serializer_class = EstadoEntregaSerializer

# Paquete ViewSet
class PaqueteViewSet(viewsets.ModelViewSet):
    queryset = Paquete.objects.all()
    serializer_class = PaqueteSerializer

# Notificación ViewSet
class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
