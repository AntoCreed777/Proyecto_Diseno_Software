from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from .models import (
    Usuario, Cliente, Conductor, Despachador, Admin,
    Vehiculo, Ruta, Paquete, Notificacion,
    TiposRoles
)
from django.contrib.auth.models import Group
from .exceptions import GroupNotConfiguredError

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    rol = serializers.ChoiceField(choices=TiposRoles.choices, read_only=True)
    is_superuser = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'telefono', 'password', 'rol', 'is_superuser']

    def get_is_superuser(self, obj):
        return obj.is_superuser

    def validate(self, attrs):
        if Usuario.objects.filter(username=attrs.get('username')).exists():
            raise serializers.ValidationError({"username": "El nombre de usuario ya está en uso."})
        if Usuario.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({"email": "El correo electrónico ya está registrado."})

        validate_password(attrs.get('password'))
        return attrs

    def create(self, validated_data):
        from accounts.views import activarEmail
        is_superuser = self.context.get('is_superuser', False)
        rol = self.context.get('rol')
        request = self.context.get('request')
        if rol not in dict(Usuario._meta.get_field('rol').choices):
            raise serializers.ValidationError({"rol": "Rol inválido."})

        password = validated_data.pop('password')

        # Crear superusuario o usuario normal
        if is_superuser:
            usuario = Usuario.objects.create_superuser(
                **validated_data,
                password=password
            )
        else:
            usuario = Usuario(**validated_data)
            usuario.set_password(password)
            usuario.save()

        # Asignar rol
        usuario.rol = rol
        usuario.save()

        # Enviar correo
        activarEmail(request=request, user=usuario)

        # Asignar grupo correspondiente
        try:
            grupo = Group.objects.get(name=rol)
            usuario.groups.add(grupo)
        except Group.DoesNotExist:
            raise GroupNotConfiguredError(f"El grupo '{rol}' no está configurado en la base de datos.")
        
        return usuario

class ClienteSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()

    class Meta:
        model = Cliente
        fields = ['id', 'usuario', 'direccion_hogar']

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')

        with transaction.atomic():
            usuario_serializer = UsuarioSerializer(
                data=usuario_data, 
                context={
                    'rol': TiposRoles.CLIENTE,
                    'request': self.context.get('request')
                }
            )
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
            usuario_serializer = UsuarioSerializer(
                data=usuario_data, 
                context={
                    'rol': TiposRoles.CONDUCTOR,
                    'request': self.context.get('request')
                }
            )
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
            usuario_serializer = UsuarioSerializer(
                data=usuario_data, 
                context={
                    'rol': TiposRoles.DESPACHADOR,
                    'request': self.context.get('request')
                }
            )
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
            usuario_serializer = UsuarioSerializer(
                data=usuario_data, 
                context={
                    'rol': TiposRoles.ADMIN,
                    'is_superuser': True,
                    'request': self.context.get('request')
                }
            )
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
    """
    Serializer para el modelo Ruta con métodos optimizados para el frontend
    """
    rutas_data = serializers.SerializerMethodField()
    rutas_data_polyline = serializers.SerializerMethodField(
        help_text="Datos de rutas usando polylines comprimidos para mayor eficiencia de red"
    )
    
    # Property calculada dinámicamente desde el modelo
    duracion_real_minutos = serializers.ReadOnlyField(
        help_text="Duración real de la ruta calculada entre fecha_inicio y fecha_fin"
    )
    
    class Meta:
        model = Ruta
        fields = '__all__'
        read_only_fields = [
            'fecha_calculo', 'distancia_total_km', 'duracion_total_minutos', 'duracion_real_minutos'
        ]
    
    def get_rutas_data(self, obj):
        """
        Devuelve los datos de rutas con coordenadas directas para el frontend
        """
        def generar_pasos_basicos(coordenadas, es_ida=True):
            """Genera pasos básicos basados en las coordenadas"""
            if not coordenadas or len(coordenadas) < 2:
                return []
            
            pasos = []
            # Paso inicial
            pasos.append({
                'nombre': 'Salida' if es_ida else 'Regreso',
                'instruccion': f'Iniciar {"ruta hacia destino" if es_ida else "ruta de regreso"}',
                'distancia': 0,
                'coordenadas': [coordenadas[0], coordenadas[1] if len(coordenadas) > 1 else coordenadas[0]]
            })
            
            # Paso intermedio (si hay suficientes coordenadas)
            if len(coordenadas) > 3:
                mitad = len(coordenadas) // 2
                pasos.append({
                    'nombre': 'Punto intermedio',
                    'instruccion': 'Continuar por la ruta establecida',
                    'distancia': 0,
                    'coordenadas': coordenadas[mitad-1:mitad+2]
                })
            
            # Paso final
            pasos.append({
                'nombre': 'Llegada' if es_ida else 'Regreso completado',
                'instruccion': f'Llegar a {"destino" if es_ida else "punto de origen"}',
                'distancia': 0,
                'coordenadas': [coordenadas[-2] if len(coordenadas) > 1 else coordenadas[-1], coordenadas[-1]]
            })
            
            return pasos
        
        return [
            {
                'coordenadas': obj.ruta_ida_coordenadas,
                'distancia_km': obj.distancia_ida_km,
                'duracion_minutos': obj.duracion_ida_minutos,
                'color': '#3388ff',
                'nombre': 'Ruta de Ida',
                'pasos': generar_pasos_basicos(obj.ruta_ida_coordenadas, es_ida=True)
            },
            {
                'coordenadas': obj.ruta_regreso_coordenadas,
                'distancia_km': obj.distancia_regreso_km,
                'duracion_minutos': obj.duracion_regreso_minutos,
                'color': '#ff8833',
                'nombre': 'Ruta de Regreso',
                'pasos': generar_pasos_basicos(obj.ruta_regreso_coordenadas, es_ida=False)
            }
        ]
    
    def get_rutas_data_polyline(self, obj):
        """
        Devuelve los datos de rutas usando polylines comprimidos (más eficiente)
        """
        return [
            {
                'polyline': obj.ruta_ida_polyline,
                'distancia_km': obj.distancia_ida_km,
                'duracion_minutos': obj.duracion_ida_minutos,
                'color': '#3388ff',
                'nombre': 'Ruta de Ida'
            },
            {
                'polyline': obj.ruta_regreso_polyline,
                'distancia_km': obj.distancia_regreso_km,
                'duracion_minutos': obj.duracion_regreso_minutos,
                'color': '#ff8833',
                'nombre': 'Ruta de Regreso'
            }
        ]

class PaqueteSerializer(serializers.ModelSerializer):
    ubicacion_actual_lat = serializers.FloatField(read_only=True)
    ubicacion_actual_lng = serializers.FloatField(read_only=True)
    ubicacion_actual_texto = serializers.CharField(read_only=True)

    class Meta:
        model = Paquete
        fields = '__all__'

    def validate_peso(self, value):
        if value <= 0:
            raise serializers.ValidationError("El peso debe ser mayor a 0.")
        if value > 1000:
            raise serializers.ValidationError("El peso no puede superar los 1000 kg.")
        return value

    def validate_largo(self, value):
        if value <= 0:
            raise serializers.ValidationError("El largo debe ser mayor a 0.")
        if value > 300:
            raise serializers.ValidationError("El largo no puede superar los 300 cm.")
        return value

    def validate_ancho(self, value):
        if value <= 0:
            raise serializers.ValidationError("El ancho debe ser mayor a 0.")
        if value > 300:
            raise serializers.ValidationError("El ancho no puede superar los 300 cm.")
        return value

    def validate_alto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El alto debe ser mayor a 0.")
        if value > 300:
            raise serializers.ValidationError("El alto no puede superar los 300 cm.")
        return value

    def validate_nombre_destinatario(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("El nombre del destinatario es obligatorio.")
        if len(value) > 255:
            raise serializers.ValidationError("El nombre del destinatario no puede superar los 255 caracteres.")
        return value

    def validate_rut_destinatario(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("El RUT del destinatario es obligatorio.")
        if len(value) > 20:
            raise serializers.ValidationError("El RUT no puede superar los 20 caracteres.")
        return value

    def validate_direccion_envio_texto(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("La dirección de envío es obligatoria.")
        if len(value) > 200:
            raise serializers.ValidationError("La dirección de envío no puede superar los 200 caracteres.")
        return value

    def validate(self, attrs):
        fecha_registro = attrs.get('fecha_registro')
        fecha_entrega = attrs.get('fecha_entrega')
        if fecha_registro and fecha_entrega and fecha_entrega < fecha_registro:
            raise serializers.ValidationError("La fecha de entrega debe ser posterior a la fecha de registro.")
        return attrs

    def create(self, validated_data):
        """
        Crea un paquete y calcula automáticamente su ruta
        """
        paquete = super().create(validated_data)
        
        # Calcular y guardar la ruta automáticamente
        try:
            from maps.utilities import calcular_y_guardar_ruta_paquete
            ruta, error = calcular_y_guardar_ruta_paquete(paquete)
            
            if error:
                # No fallar la creación del paquete por errores de ruta
                pass
                
        except Exception as e:
            # No fallar la creación del paquete por errores de ruta
            pass
        
        return paquete
    
    def update(self, instance, validated_data):
        """
        Actualiza un paquete y recalcula la ruta si la dirección cambió
        """
        direccion_anterior = instance.direccion_envio_texto
        paquete = super().update(instance, validated_data)
        
        # Si cambió la dirección de envío, recalcular la ruta
        if paquete.direccion_envio_texto != direccion_anterior:
            try:
                from maps.utilities import calcular_y_guardar_ruta_paquete
                calcular_y_guardar_ruta_paquete(paquete)
            except Exception:
                # No fallar la actualización por errores de ruta
                pass
        
        return paquete

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'
