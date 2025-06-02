from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import (
    Usuario, Cliente, Conductor, Admin, Vehiculo,
    Ruta, ConductorPoseeRuta, EstadoEntrega, Paquete,
    Notificacion
)

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'rol']

    def validate(self, attrs):
        if Usuario.objects.filter(username=attrs.get('username')).exists():
            raise serializers.ValidationError({"username": "El nombre de usuario ya está en uso."})
        if Usuario.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({"email": "El correo electrónico ya está registrado."})

        validate_password(attrs.get('password'))
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario

class ClienteSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()

    class Meta:
        model = Cliente
        fields = ['id', 'usuario', 'direccion_hogar']

    def validate_direccion_hogar(self, value):
        if not value:
            raise serializers.ValidationError("La dirección del hogar es obligatoria.")
        return value

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')
        usuario_serializer = UsuarioSerializer(data=usuario_data)
        usuario_serializer.is_valid(raise_exception=True)
        usuario = usuario_serializer.save()
        return Cliente.objects.create(usuario=usuario, **validated_data)

class UsuarioClienteSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username')
    email = serializers.EmailField(source='usuario.email')
    first_name = serializers.CharField(source='usuario.first_name')
    last_name = serializers.CharField(source='usuario.last_name')
    rol = serializers.ChoiceField(choices=Usuario._meta.get_field('rol').choices, source='usuario.rol')
    password = serializers.CharField(source='usuario.password', write_only=True, required=True)

    class Meta:
        model = Cliente
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'rol', 'direccion_hogar', 'password']

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')
        usuario_serializer = UsuarioSerializer(data=usuario_data)
        usuario_serializer.is_valid(raise_exception=True)
        usuario = usuario_serializer.save()
        return Cliente.objects.create(usuario=usuario, **validated_data)

class ConductorSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()

    class Meta:
        model = Conductor
        fields = ['id', 'usuario', 'vehiculo']

    def validate_vehiculo(self, value):
        if not value:
            raise serializers.ValidationError("El vehículo es obligatorio.")
        return value

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')
        usuario_serializer = UsuarioSerializer(data=usuario_data)
        usuario_serializer.is_valid(raise_exception=True)
        usuario = usuario_serializer.save()
        return Conductor.objects.create(usuario=usuario, **validated_data)

class UsuarioConductorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username')
    email = serializers.EmailField(source='usuario.email')
    first_name = serializers.CharField(source='usuario.first_name')
    last_name = serializers.CharField(source='usuario.last_name')
    rol = serializers.ChoiceField(choices=Usuario._meta.get_field('rol').choices, source='usuario.rol')
    matricula_vehiculo = serializers.CharField(source='vehiculo.matricula', read_only=True)
    password = serializers.CharField(source='usuario.password', write_only=True, required=True)

    class Meta:
        model = Conductor
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'rol', 'matricula_vehiculo', 'password']

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')
        usuario_serializer = UsuarioSerializer(data=usuario_data)
        usuario_serializer.is_valid(raise_exception=True)
        usuario = usuario_serializer.save()
        return Conductor.objects.create(usuario=usuario, **validated_data)

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
        usuario_serializer = UsuarioSerializer(data=usuario_data)
        usuario_serializer.is_valid(raise_exception=True)
        usuario = usuario_serializer.save()
        return Admin.objects.create(usuario=usuario, **validated_data)

class UsuarioAdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username')
    email = serializers.EmailField(source='usuario.email')
    first_name = serializers.CharField(source='usuario.first_name')
    last_name = serializers.CharField(source='usuario.last_name')
    rol = serializers.ChoiceField(choices=Usuario._meta.get_field('rol').choices, source='usuario.rol')
    password = serializers.CharField(source='usuario.password', write_only=True, required=True)

    class Meta:
        model = Admin
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'rol', 'nivel_acceso', 'password']

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')
        usuario_serializer = UsuarioSerializer(data=usuario_data)
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

class EstadoEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoEntrega
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
