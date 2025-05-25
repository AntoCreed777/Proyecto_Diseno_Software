from rest_framework import serializers
from .models import *

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        extra_kwargs = {
            'contraseña': {'write_only': True}
        }

    def create(self, validated_data):
        user = Cliente(**validated_data)
        user.set_password(validated_data['contraseña'])
        user.save()
        return user
    
class ConductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conductor
        fields = '__all__'
        extra_kwargs = {
            'contraseña': {'write_only': True}
        }

    def create(self, validated_data):
        user = Conductor(**validated_data)
        user.set_password(validated_data['contraseña'])
        user.save()
        return user
    
class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'
        extra_kwargs = {
            'contraseña': {'write_only': True}
        }

    def create(self, validated_data):
        user = Admin(**validated_data)
        user.set_password(validated_data['contraseña'])
        user.save()
        return user
    
class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = '__all__'
        extra_kwargs = {
            'conductor': {'required': False}
        }
    def create(self, validated_data):
        vehiculo = Vehiculo(**validated_data)
        vehiculo.save()
        return vehiculo
    
class RutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ruta
        fields = '__all__'

    def create(self, validated_data):
        ruta = Ruta(**validated_data)
        ruta.save()
        return ruta
    
class PaqueteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paquete
        fields = '__all__'

    def create(self, validated_data):
        paquete = Paquete(**validated_data)
        paquete.save()
        return paquete
    
class EstadoEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoEntrega
        fields = '__all__'

    def create(self, validated_data):
        estado_entrega = EstadoEntrega(**validated_data)
        estado_entrega.save()
        return estado_entrega
    
class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'

    def create(self, validated_data):
        notificacion = Notificacion(**validated_data)
        notificacion.save()
        return notificacion
    
class EntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrega
        fields = '__all__'

    def create(self, validated_data):
        entrega = Entrega(**validated_data)
        entrega.save()
        return entrega
