from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import (
    Usuario, Cliente, Conductor, Despachador, Admin,
    Vehiculo, Ruta, ConductorPoseeRuta, Paquete, Notificacion
)
from .serializers import (
    UsuarioSerializer, ClienteSerializer,
    ConductorSerializer, DespachadorSerializer, AdminSerializer,
    VehiculoSerializer, RutaSerializer, ConductorPoseeRutaSerializer,
    PaqueteSerializer, NotificacionSerializer
)
from rest_framework.response import Response
from rest_framework import status

class UsuarioViewSet(ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    #permission_classes = [IsAuthenticated]

    
    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "No puedes crear usuarios directamente desde esta API."}, 
            status=status.HTTP_403_FORBIDDEN
        )

class ClienteViewSet(ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    #permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        # Incluir el request en el contexto del serializador
        kwargs['context'] = self.get_serializer_context()
        return super().get_serializer(*args, **kwargs)

    def get_serializer_context(self):
        # Agregar el request al contexto
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ConductorViewSet(ModelViewSet):
    queryset = Conductor.objects.all()
    serializer_class = ConductorSerializer
    #permission_classes = [IsAuthenticated]
    
    def get_serializer(self, *args, **kwargs):
        # Incluir el request en el contexto del serializador
        kwargs['context'] = self.get_serializer_context()
        return super().get_serializer(*args, **kwargs)

    def get_serializer_context(self):
        # Agregar el request al contexto
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class DespachadorViewSet(ModelViewSet):
    queryset = Despachador.objects.all()
    serializer_class = DespachadorSerializer
    #permission_classes = [IsAuthenticated]
    
    def get_serializer(self, *args, **kwargs):
        # Incluir el request en el contexto del serializador
        kwargs['context'] = self.get_serializer_context()
        return super().get_serializer(*args, **kwargs)

    def get_serializer_context(self):
        # Agregar el request al contexto
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class AdminViewSet(ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    #permission_classes = [IsAuthenticated]
    
    def get_serializer(self, *args, **kwargs):
        # Incluir el request en el contexto del serializador
        kwargs['context'] = self.get_serializer_context()
        return super().get_serializer(*args, **kwargs)

    def get_serializer_context(self):
        # Agregar el request al contexto
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

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

class PaqueteViewSet(ModelViewSet):
    queryset = Paquete.objects.all()
    serializer_class = PaqueteSerializer
    #permission_classes = [IsAuthenticated]

class NotificacionViewSet(ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    #permission_classes = [IsAuthenticated]
