from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from .models import (
    Usuario, Cliente, Conductor, Despachador, Admin,
    Vehiculo, Ruta, ConductorPoseeRuta, Paquete, Notificacion,
    TiposRoles
)
from django.contrib.auth.models import Group
from .exceptions import GroupNotConfiguredError

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    rol = serializers.ChoiceField(choices=TiposRoles.choices, read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'telefono', 'password', 'rol']

    def validate(self, attrs):
        if Usuario.objects.filter(username=attrs.get('username')).exists():
            raise serializers.ValidationError({"username": "El nombre de usuario ya está en uso."})
        if Usuario.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({"email": "El correo electrónico ya está registrado."})

        validate_password(attrs.get('password'))
        return attrs

    def create(self, validated_data):
        rol = self.context.get('rol')
        if rol not in dict(Usuario._meta.get_field('rol').choices):
            raise serializers.ValidationError({"rol": "Rol inválido."})

        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.rol = rol
        usuario.set_password(password)
        usuario.save()

        try:
            grupo = Group.objects.get(name=rol)
        except Group.DoesNotExist:
            raise GroupNotConfiguredError(f"El grupo '{rol}' no está configurado en la base de datos.")
        usuario.groups.add(grupo)
        
        return usuario

class ClienteSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()

    class Meta:
        model = Cliente
        fields = ['id', 'usuario', 'direccion_hogar']

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')

        with transaction.atomic():
            usuario_serializer = UsuarioSerializer(data=usuario_data, context={'rol': TiposRoles.CLIENTE})
            usuario_serializer.is_valid(raise_exception=True)
            usuario = usuario_serializer.save()

            return Cliente.objects.create(usuario=usuario, **validated_data)

class ConductorSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()
    estado = serializers.ChoiceField(choices=Conductor._meta.get_field('estado').choices, read_only=True)

    class Meta:
        model = Conductor
        fields = ['id', 'usuario', 'vehiculo', 'estado']

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')

        with transaction.atomic():
            usuario_serializer = UsuarioSerializer(data=usuario_data, context={'rol': TiposRoles.CONDUCTOR})
            usuario_serializer.is_valid(raise_exception=True)
            usuario = usuario_serializer.save()

            return Conductor.objects.create(usuario=usuario, estado='disponible', **validated_data)

class DespachadorSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()

    class Meta:
        model = Despachador
        fields = ['id', 'usuario']

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')
        with transaction.atomic():
            usuario_serializer = UsuarioSerializer(data=usuario_data, context={'rol': TiposRoles.DESPACHADOR})
            usuario_serializer.is_valid(raise_exception=True)
            usuario = usuario_serializer.save()

            return Despachador.objects.create(usuario=usuario, **validated_data)

class AdminSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()

    class Meta:
        model = Admin
        fields = ['id', 'usuario', 'nivel_acceso']

    def validate_nivel_acceso(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("El nivel de acceso debe estar entre 1 y 5.")
        return value

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')

        with transaction.atomic():
            usuario_serializer = UsuarioSerializer(data=usuario_data, context={'rol': TiposRoles.ADMIN})
            usuario_serializer.is_valid(raise_exception=True)
            usuario = usuario_serializer.save()

            return Admin.objects.create(usuario=usuario, **validated_data)

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = '__all__'

    def validate_matricula(self, value):
        if not value:
            raise serializers.ValidationError("La matrícula es obligatoria.")
        if Vehiculo.objects.filter(matricula=value).exists():
            raise serializers.ValidationError("La matrícula ya está registrada.")
        return value

class RutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ruta
        fields = '__all__'

class ConductorPoseeRutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConductorPoseeRuta
        fields = '__all__'

class PaqueteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paquete
        fields = '__all__'

    def validate_peso(self, value):
        if value <= 0:
            raise serializers.ValidationError("El peso debe ser mayor a 0.")
        return value

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'
