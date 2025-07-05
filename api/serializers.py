"""
Serializers de la aplicación API para sistema de gestión de paquetes y rutas.

Este archivo contiene todos los serializers de Django REST Framework que
manejan la serialización/deserialización de los modelos para la API REST.
Incluye validaciones personalizadas y lógica de creación para cada entidad.
"""

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
    """
    Serializer base para el modelo Usuario.
    
    Maneja la creación de usuarios con diferentes roles y validaciones
    de integridad. Incluye lógica para asignación de grupos y envío de
    correos de activación.
    
    Campos especiales:
    - password: Solo escritura, validado con validadores de Django
    - rol: Solo lectura, se asigna automáticamente según el contexto
    - is_superuser: Campo calculado para indicar permisos administrativos
    """
    
    # Solo escritura para mayor seguridad
    password = serializers.CharField(
        write_only=True, 
        required=True,
        help_text="Contraseña del usuario (mínimo 8 caracteres)"
    )
    
    # Solo lectura, se asigna automáticamente
    rol = serializers.ChoiceField(
        choices=TiposRoles.choices, 
        read_only=True,
        help_text="Rol del usuario en el sistema"
    )
    
    # Campo calculado dinámicamente
    is_superuser = serializers.SerializerMethodField(
        help_text="Indica si el usuario tiene permisos de superusuario"
    )

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'telefono', 'password', 'rol', 'is_superuser']

    def get_is_superuser(self, obj):
        """Determina si el usuario tiene permisos de superusuario."""
        return obj.is_superuser

    def validate(self, attrs):
        """
        Validaciones a nivel de serializer para unicidad de username y email.
        También valida la fortaleza de la contraseña usando validadores de Django.
        """
        if Usuario.objects.filter(username=attrs.get('username')).exists():
            raise serializers.ValidationError({"username": "El nombre de usuario ya está en uso."})
        if Usuario.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({"email": "El correo electrónico ya está registrado."})

        validate_password(attrs.get('password'))
        return attrs

    def create(self, validated_data):
        """
        Crea un usuario con el rol especificado en el contexto.
        
        Pasos del proceso:
        1. Extrae el rol y configuración del contexto
        2. Crea superusuario o usuario normal según configuración
        3. Asigna el rol al usuario
        4. Envía correo de activación
        5. Asigna al grupo correspondiente del rol
        
        Args:
            validated_data: Datos validados del usuario
            
        Returns:
            Usuario: Instancia del usuario creado
            
        Raises:
            ValidationError: Si el rol es inválido
            GroupNotConfiguredError: Si el grupo del rol no existe
        """
        from accounts.views import activarEmail
        is_superuser = self.context.get('is_superuser', False)
        rol = self.context.get('rol')
        request = self.context.get('request')
        
        if rol not in [choice[0] for choice in TiposRoles.choices]:
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

        # Enviar correo de activación
        activarEmail(request=request, user=usuario)

        # Asignar grupo correspondiente al rol
        try:
            grupo = Group.objects.get(name=rol)
            usuario.groups.add(grupo)
        except Group.DoesNotExist:
            raise GroupNotConfiguredError(f"El grupo '{rol}' no está configurado en la base de datos.")
        
        return usuario

class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Cliente.
    
    Maneja la creación de clientes incluyendo la creación automática del
    usuario asociado. Utiliza transacciones para garantizar la integridad
    de los datos durante el proceso de creación.
    
    Campos anidados:
    - usuario: Serializer anidado que maneja toda la información del usuario
    """
    
    # Serializer anidado para manejar datos completos del usuario
    usuario = UsuarioSerializer(
        help_text="Información completa del usuario asociado al cliente"
    )

    class Meta:
        model = Cliente
        fields = ['id', 'usuario', 'direccion_hogar']

    def create(self, validated_data):
        """
        Crea un cliente junto con su usuario asociado en una transacción atómica.
        
        Proceso:
        1. Extrae los datos del usuario anidado
        2. Crea el usuario con rol CLIENTE usando UsuarioSerializer
        3. Crea el cliente asociándolo al usuario creado
        
        Args:
            validated_data: Datos validados del cliente y usuario anidado
            
        Returns:
            Cliente: Instancia del cliente creado con usuario asociado
        """
        usuario_data = validated_data.pop('usuario')

        with transaction.atomic():
            # Crear usuario con rol de cliente
            usuario_serializer = UsuarioSerializer(
                data=usuario_data, 
                context={
                    'rol': TiposRoles.CLIENTE,
                    'request': self.context.get('request')
                }
            )
            usuario_serializer.is_valid(raise_exception=True)
            usuario = usuario_serializer.save()

            # Crear cliente asociado al usuario
            return Cliente.objects.create(usuario=usuario, **validated_data)

class ConductorSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Conductor.
    
    Maneja la creación de conductores con estado inicial 'disponible'.
    Incluye la creación automática del usuario asociado y la asignación
    del rol CONDUCTOR correspondiente.
    
    Campos especiales:
    - usuario: Serializer anidado para datos completos del usuario
    - estado: Solo lectura, se inicializa automáticamente como 'disponible'
    """
    
    # Serializer anidado para manejar datos completos del usuario
    usuario = UsuarioSerializer(
        help_text="Información completa del usuario asociado al conductor"
    )
    
    # Solo lectura, se asigna automáticamente al crear
    estado = serializers.ChoiceField(
        choices=Conductor._meta.get_field('estado').choices, 
        read_only=True,
        help_text="Estado actual del conductor (se inicializa como 'disponible')"
    )

    class Meta:
        model = Conductor
        fields = ['id', 'usuario', 'vehiculo', 'estado']

    def create(self, validated_data):
        """
        Crea un conductor junto con su usuario asociado en una transacción atómica.
        
        El conductor se crea con estado inicial 'disponible' independientemente
        de cualquier valor enviado en los datos.
        
        Proceso:
        1. Extrae los datos del usuario anidado
        2. Crea el usuario con rol CONDUCTOR usando UsuarioSerializer
        3. Crea el conductor con estado 'disponible'
        
        Args:
            validated_data: Datos validados del conductor y usuario anidado
            
        Returns:
            Conductor: Instancia del conductor creado con usuario asociado
        """
        usuario_data = validated_data.pop('usuario')

        with transaction.atomic():
            # Crear usuario con rol de conductor
            usuario_serializer = UsuarioSerializer(
                data=usuario_data, 
                context={
                    'rol': TiposRoles.CONDUCTOR,
                    'request': self.context.get('request')
                }
            )
            usuario_serializer.is_valid(raise_exception=True)
            usuario = usuario_serializer.save()

            # Crear conductor con estado inicial 'disponible'
            return Conductor.objects.create(usuario=usuario, estado='disponible', **validated_data)

class DespachadorSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Despachador.
    
    Maneja la creación de despachadores que son responsables de la
    gestión y asignación de rutas y paquetes. Incluye la creación
    automática del usuario asociado con el rol DESPACHADOR.
    
    Campos anidados:
    - usuario: Serializer anidado para datos completos del usuario
    """
    
    # Serializer anidado para manejar datos completos del usuario
    usuario = UsuarioSerializer(
        help_text="Información completa del usuario asociado al despachador"
    )

    class Meta:
        model = Despachador
        fields = ['id', 'usuario']

    def create(self, validated_data):
        """
        Crea un despachador junto con su usuario asociado en una transacción atómica.
        
        Proceso:
        1. Extrae los datos del usuario anidado
        2. Crea el usuario con rol DESPACHADOR usando UsuarioSerializer
        3. Crea el despachador asociándolo al usuario creado
        
        Args:
            validated_data: Datos validados del despachador y usuario anidado
            
        Returns:
            Despachador: Instancia del despachador creado con usuario asociado
        """
        usuario_data = validated_data.pop('usuario')
        
        with transaction.atomic():
            # Crear usuario con rol de despachador
            usuario_serializer = UsuarioSerializer(
                data=usuario_data, 
                context={
                    'rol': TiposRoles.DESPACHADOR,
                    'request': self.context.get('request')
                }
            )
            usuario_serializer.is_valid(raise_exception=True)
            usuario = usuario_serializer.save()

            # Crear despachador asociado al usuario
            return Despachador.objects.create(usuario=usuario, **validated_data)

class AdminSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Admin.
    
    Maneja la creación de administradores con permisos de superusuario.
    Incluye validación del nivel de acceso y creación automática del
    usuario asociado con privilegios administrativos.
    
    Campos especiales:
    - usuario: Serializer anidado para datos completos del usuario
    - nivel_acceso: Validado para estar en el rango 1-5
    
    Nota: Los administradores se crean automáticamente como superusuarios.
    """
    
    # Serializer anidado para manejar datos completos del usuario
    usuario = UsuarioSerializer(
        help_text="Información completa del usuario asociado al administrador"
    )

    class Meta:
        model = Admin
        fields = ['id', 'usuario', 'nivel_acceso']

    def validate_nivel_acceso(self, value):
        """
        Valida que el nivel de acceso esté en el rango permitido.
        
        Args:
            value: Valor del nivel de acceso a validar
            
        Returns:
            int: Valor validado del nivel de acceso
            
        Raises:
            ValidationError: Si el nivel no está entre 1 y 5
        """
        if not 1 <= value <= 5:
            raise serializers.ValidationError("El nivel de acceso debe estar entre 1 y 5.")
        return value

    def create(self, validated_data):
        """
        Crea un administrador junto con su usuario asociado como superusuario.
        
        Proceso:
        1. Extrae los datos del usuario anidado
        2. Crea el usuario con rol ADMIN y permisos de superusuario
        3. Crea el administrador asociándolo al usuario creado
        
        Args:
            validated_data: Datos validados del administrador y usuario anidado
            
        Returns:
            Admin: Instancia del administrador creado con usuario superusuario asociado
        """
        usuario_data = validated_data.pop('usuario')

        with transaction.atomic():
            # Crear usuario con rol de admin y permisos de superusuario
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

            # Crear administrador asociado al usuario
            return Admin.objects.create(usuario=usuario, **validated_data)

class VehiculoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Vehiculo.
    
    Maneja la serialización y validación de vehículos del sistema.
    Incluye validación de unicidad de matrícula para evitar duplicados.
    
    Validaciones implementadas:
    - Matrícula obligatoria y única en el sistema
    """
    
    class Meta:
        model = Vehiculo
        fields = '__all__'

    def validate_matricula(self, value):
        """
        Valida que la matrícula sea obligatoria y única en el sistema.
        
        Args:
            value: Valor de la matrícula a validar
            
        Returns:
            str: Matrícula validada
            
        Raises:
            ValidationError: Si la matrícula está vacía o ya existe
        """
        if not value:
            raise serializers.ValidationError("La matrícula es obligatoria.")
        if Vehiculo.objects.filter(matricula=value).exists():
            raise serializers.ValidationError("La matrícula ya está registrada.")
        return value

class RutaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Ruta con métodos optimizados para el frontend.
    
    Proporciona datos de rutas en múltiples formatos para diferentes casos de uso:
    - Coordenadas directas para mapas interactivos
    - Polylines comprimidos para mayor eficiencia de red
    - Duración real calculada dinámicamente
    
    Campos especiales:
    - rutas_data: Datos completos de rutas con coordenadas y pasos
    - rutas_data_polyline: Datos de rutas usando polylines comprimidos
    - duracion_real_minutos: Duración calculada entre fecha_inicio y fecha_fin
    
    Campos de solo lectura:
    - fecha_calculo: Se asigna automáticamente al calcular la ruta
    - distancia_total_km: Calculada automáticamente por el sistema de mapas
    - duracion_total_minutos: Calculada automáticamente por el sistema de mapas
    - duracion_real_minutos: Property calculada dinámicamente
    """
    
    # Datos de rutas con coordenadas completas para mapas interactivos
    rutas_data = serializers.SerializerMethodField(
        help_text="Datos completos de rutas con coordenadas, distancias y pasos detallados"
    )
    
    # Datos de rutas usando polylines para mayor eficiencia
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
        Devuelve los datos de rutas con coordenadas directas para el frontend.
        
        Genera pasos básicos de navegación basados en las coordenadas
        almacenadas, proporcionando una estructura completa para
        renderizado en mapas interactivos.
        
        Args:
            obj: Instancia del modelo Ruta
            
        Returns:
            list: Lista con datos de ruta de ida y regreso, incluyendo:
                - coordenadas: Array de coordenadas [lat, lng]
                - distancia_km: Distancia en kilómetros
                - duracion_minutos: Duración estimada en minutos
                - color: Color para renderización en mapa
                - nombre: Nombre descriptivo de la ruta
                - pasos: Lista de pasos de navegación generados
        """
        def generar_pasos_basicos(coordenadas, es_ida=True):
            """
            Genera pasos básicos basados en las coordenadas.
            
            Crea una estructura de navegación simple con puntos de:
            - Salida/Regreso
            - Punto intermedio (si hay suficientes coordenadas)
            - Llegada/Regreso completado
            
            Args:
                coordenadas: Lista de coordenadas [lat, lng]
                es_ida: True para ruta de ida, False para regreso
                
            Returns:
                list: Lista de pasos de navegación
            """
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
        Devuelve los datos de rutas usando polylines comprimidos (más eficiente).
        
        Utiliza polylines codificados para reducir el tamaño de los datos
        transmitidos, especialmente útil para aplicaciones móviles o
        conexiones con ancho de banda limitado.
        
        Args:
            obj: Instancia del modelo Ruta
            
        Returns:
            list: Lista con datos de ruta usando polylines, incluyendo:
                - polyline: Polyline codificado de la ruta
                - distancia_km: Distancia en kilómetros
                - duracion_minutos: Duración estimada en minutos
                - color: Color para renderización en mapa
                - nombre: Nombre descriptivo de la ruta
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
    """
    Serializer para el modelo Paquete.
    
    Maneja la serialización completa de paquetes incluyendo validaciones
    exhaustivas de dimensiones, peso y datos del destinatario. Incluye
    lógica automática para el cálculo de rutas cuando se crean o actualizan
    las direcciones de envío.
    
    Campos de ubicación:
    - ubicacion_actual_lat: Latitud actual del paquete (solo lectura)
    - ubicacion_actual_lng: Longitud actual del paquete (solo lectura)
    - ubicacion_actual_texto: Descripción textual de la ubicación (solo lectura)
    
    Validaciones implementadas:
    - Peso: Entre 0.1 y 1000 kg
    - Dimensiones: Entre 0.1 y 300 cm para largo, ancho y alto
    - Datos del destinatario: Nombre y RUT obligatorios
    - Dirección de envío: Obligatoria y con límite de caracteres
    - Fechas: La fecha de entrega debe ser posterior a la de registro
    
    Funcionalidades automáticas:
    - Cálculo de ruta al crear el paquete
    - Recálculo de ruta al cambiar la dirección de envío
    """
    
    # Campos de ubicación de solo lectura (calculados automáticamente)
    ubicacion_actual_lat = serializers.FloatField(
        read_only=True,
        help_text="Latitud actual del paquete en tiempo real"
    )
    ubicacion_actual_lng = serializers.FloatField(
        read_only=True,
        help_text="Longitud actual del paquete en tiempo real"
    )
    ubicacion_actual_texto = serializers.CharField(
        read_only=True,
        help_text="Descripción textual de la ubicación actual del paquete"
    )
    direccion_envio_lat = serializers.FloatField(
        read_only=True,
        help_text="Latitud de la dirección de envío"
    )
    direccion_envio_lng = serializers.FloatField(
        read_only=True,
        help_text="Longitud de la dirección de envío"
    )

    class Meta:
        model = Paquete
        fields = '__all__'

    def validate_peso(self, value):
        """
        Valida que el peso esté dentro del rango permitido.
        
        Args:
            value: Peso en kilogramos a validar
            
        Returns:
            float: Peso validado
            
        Raises:
            ValidationError: Si el peso está fuera del rango 0.1-1000 kg
        """
        if value <= 0:
            raise serializers.ValidationError("El peso debe ser mayor a 0.")
        if value > 1000:
            raise serializers.ValidationError("El peso no puede superar los 1000 kg.")
        return value

    def validate_largo(self, value):
        """
        Valida que el largo esté dentro del rango permitido.
        
        Args:
            value: Largo en centímetros a validar
            
        Returns:
            float: Largo validado
            
        Raises:
            ValidationError: Si el largo está fuera del rango 0.1-300 cm
        """
        if value <= 0:
            raise serializers.ValidationError("El largo debe ser mayor a 0.")
        if value > 300:
            raise serializers.ValidationError("El largo no puede superar los 300 cm.")
        return value

    def validate_ancho(self, value):
        """
        Valida que el ancho esté dentro del rango permitido.
        
        Args:
            value: Ancho en centímetros a validar
            
        Returns:
            float: Ancho validado
            
        Raises:
            ValidationError: Si el ancho está fuera del rango 0.1-300 cm
        """
        if value <= 0:
            raise serializers.ValidationError("El ancho debe ser mayor a 0.")
        if value > 300:
            raise serializers.ValidationError("El ancho no puede superar los 300 cm.")
        return value

    def validate_alto(self, value):
        """
        Valida que el alto esté dentro del rango permitido.
        
        Args:
            value: Alto en centímetros a validar
            
        Returns:
            float: Alto validado
            
        Raises:
            ValidationError: Si el alto está fuera del rango 0.1-300 cm
        """
        if value <= 0:
            raise serializers.ValidationError("El alto debe ser mayor a 0.")
        if value > 300:
            raise serializers.ValidationError("El alto no puede superar los 300 cm.")
        return value

    def validate_nombre_destinatario(self, value):
        """
        Valida que el nombre del destinatario sea válido.
        
        Args:
            value: Nombre del destinatario a validar
            
        Returns:
            str: Nombre validado
            
        Raises:
            ValidationError: Si el nombre está vacío o excede 100 caracteres
        """
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("El nombre del destinatario es obligatorio.")
        if len(value) > 100:
            raise serializers.ValidationError("El nombre del destinatario no puede superar los 100 caracteres.")
        return value

    def validate_rut_destinatario(self, value):
        """
        Valida que el RUT del destinatario sea válido.
        
        Args:
            value: RUT del destinatario a validar
            
        Returns:
            str: RUT validado
            
        Raises:
            ValidationError: Si el RUT está vacío, excede 12 caracteres
        """
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("El RUT del destinatario es obligatorio.")
        if len(value) > 12:
            raise serializers.ValidationError("El RUT no puede superar los 12 caracteres.")
        return value

    def validate_direccion_envio_texto(self, value):
        """
        Valida que la dirección de envío sea válida.
        
        Args:
            value: Dirección de envío a validar
            
        Returns:
            str: Dirección validada
            
        Raises:
            ValidationError: Si la dirección está vacía o excede 200 caracteres
        """
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("La dirección de envío es obligatoria.")
        if len(value) > 200:
            raise serializers.ValidationError("La dirección de envío no puede superar los 200 caracteres.")
        return value

    def validate(self, attrs):
        """
        Validaciones a nivel de objeto completo.
        
        Valida que las fechas tengan coherencia temporal:
        - La fecha de entrega debe ser posterior a la fecha de registro
        
        Args:
            attrs: Diccionario con todos los atributos validados
            
        Returns:
            dict: Atributos validados
            
        Raises:
            ValidationError: Si las fechas no son coherentes
        """
        fecha_registro = attrs.get('fecha_registro')
        fecha_entrega = attrs.get('fecha_entrega')
        if fecha_registro and fecha_entrega and fecha_entrega < fecha_registro:
            raise serializers.ValidationError("La fecha de entrega debe ser posterior a la fecha de registro.")
        return attrs

    def create(self, validated_data):
        """
        Crea un paquete y calcula automáticamente su ruta.
        
        Primero intenta geocodificar la dirección, luego crea el paquete
        y finalmente calcula la ruta completa.
        
        Args:
            validated_data: Datos validados del paquete
            
        Returns:
            Paquete: Instancia del paquete creado
        """
        from maps.constants import UNIVERSIDAD_CONCEPCION_COORDS_TUPLE
        
        # Primero intentar geocodificar la dirección de envío
        direccion_texto = validated_data.get('direccion_envio_texto', '')
        coordenadas_calculadas = None
        
        if direccion_texto:
            try:
                from maps.utilities import obtener_coordenadas
                coordenadas_calculadas = obtener_coordenadas(direccion_texto)
            except Exception:
                pass
        
        # Establecer coordenadas (geocodificadas o por defecto)
        if coordenadas_calculadas:
            validated_data['direccion_envio_lat'] = coordenadas_calculadas[0]
            validated_data['direccion_envio_lng'] = coordenadas_calculadas[1]
        else:
            validated_data['direccion_envio_lat'] = UNIVERSIDAD_CONCEPCION_COORDS_TUPLE[0]
            validated_data['direccion_envio_lng'] = UNIVERSIDAD_CONCEPCION_COORDS_TUPLE[1]
        
        # Crear y guardar el paquete
        paquete = Paquete(**validated_data)
        paquete.save()
        
        # Intentar calcular la ruta completa después de guardar el paquete
        try:
            from maps.utilities import calcular_y_guardar_ruta_paquete
            ruta, error = calcular_y_guardar_ruta_paquete(paquete)
            
            if ruta and not error:
                # Actualizar coordenadas si la ruta se calculó exitosamente
                paquete.direccion_envio_lat = ruta.destino_lat
                paquete.direccion_envio_lng = ruta.destino_lng
                paquete.save()
        except Exception as e:
            # Si falla el cálculo de ruta, mantener las coordenadas geocodificadas
            pass
        
        return paquete
    
    def update(self, instance, validated_data):
        """
        Actualiza un paquete y recalcula la ruta si la dirección cambió.
        
        Si la dirección de envío ha cambiado, recalcula automáticamente
        la ruta. Si ocurre un error en el recálculo, intenta geocodificar
        la nueva dirección.
        
        Args:
            instance: Instancia actual del paquete
            validated_data: Datos validados para la actualización
            
        Returns:
            Paquete: Instancia del paquete actualizado
        """
        direccion_anterior = instance.direccion_envio_texto
        paquete = super().update(instance, validated_data)
        
        # Si cambió la dirección de envío, recalcular la ruta
        if paquete.direccion_envio_texto != direccion_anterior:
            try:
                from maps.utilities import calcular_y_guardar_ruta_paquete
                ruta, error = calcular_y_guardar_ruta_paquete(paquete)
                
                if ruta and not error:
                    # Actualizar coordenadas si la ruta se calculó exitosamente
                    paquete.direccion_envio_lat = ruta.destino_lat
                    paquete.direccion_envio_lng = ruta.destino_lng
                    paquete.save()
            except Exception:
                # Si falla el cálculo de ruta, intentar geocodificar la nueva dirección
                try:
                    from maps.utilities import obtener_coordenadas
                    coordenadas = obtener_coordenadas(paquete.direccion_envio_texto)
                    if coordenadas:
                        paquete.direccion_envio_lat = coordenadas[0]
                        paquete.direccion_envio_lng = coordenadas[1]
                        paquete.save()
                except Exception:
                    # Si todo falla, mantener las coordenadas actuales
                    pass
        
        return paquete

class NotificacionSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Notificacion.
    
    Maneja la serialización de notificaciones del sistema que se envían
    a los clientes para informar sobre el estado de sus paquetes y otros
    eventos relevantes del sistema de gestión de envíos.
    
    Características:
    - Serialización completa de todos los campos del modelo
    - Sin validaciones personalizadas adicionales (usa las del modelo)
    - Soporte para relaciones con Cliente y Paquete
    
    Campos relacionados:
    - cliente: ForeignKey hacia el cliente que recibe la notificación
    - paquete: ForeignKey opcional hacia el paquete relacionado
    """
    
    class Meta:
        model = Notificacion
        fields = '__all__'
