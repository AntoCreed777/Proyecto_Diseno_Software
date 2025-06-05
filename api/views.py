from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import (
    Usuario, Cliente, Conductor, Despachador, Admin,
    Vehiculo, Ruta, ConductorPoseeRuta, EstadoEntrega,
    Paquete, Notificacion
)
from .serializers import (
    UsuarioSerializer, ClienteSerializer,
    ConductorSerializer, DespachadorSerializer, AdminSerializer,
    VehiculoSerializer, RutaSerializer,
    ConductorPoseeRutaSerializer, EstadoEntregaSerializer,
    PaqueteSerializer, NotificacionSerializer
)

class UsuarioViewSet(ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    #permission_classes = [IsAuthenticated]

class ClienteViewSet(ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    #permission_classes = [IsAuthenticated]

class ConductorViewSet(ModelViewSet):
    queryset = Conductor.objects.all()
    serializer_class = ConductorSerializer
    #permission_classes = [IsAuthenticated]

class DespachadorViewSet(ModelViewSet):
    queryset = Despachador.objects.all()
    serializer_class = DespachadorSerializer
    #permission_classes = [IsAuthenticated]

class AdminViewSet(ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    #permission_classes = [IsAuthenticated]

class VehiculoViewSet(ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    #permission_classes = [IsAuthenticated]

class RutaViewSet(ModelViewSet):
    queryset = Ruta.objects.all()
    serializer_class = RutaSerializer
    #permission_classes = [IsAuthenticated]

class ConductorPoseeRutaViewSet(ModelViewSet):
    queryset = ConductorPoseeRuta.objects.all()
    serializer_class = ConductorPoseeRutaSerializer
    #permission_classes = [IsAuthenticated]

class EstadoEntregaViewSet(ReadOnlyModelViewSet):
    queryset = EstadoEntrega.objects.all()
    serializer_class = EstadoEntregaSerializer
    #permission_classes = [IsAuthenticated]

class PaqueteViewSet(ModelViewSet):
    queryset = Paquete.objects.all()
    serializer_class = PaqueteSerializer
    #permission_classes = [IsAuthenticated]

class NotificacionViewSet(ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    #permission_classes = [IsAuthenticated]
