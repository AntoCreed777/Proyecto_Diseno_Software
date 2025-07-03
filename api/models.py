"""
Modelos de la aplicación API para sistema de gestión de paquetes y rutas.

Este archivo contiene todos los modelos de Django que representan las entidades
del sistema de gestión de envío de paquetes.
"""

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from maps.constants import UNIVERSIDAD_CONCEPCION, UNIVERSIDAD_CONCEPCION_COORDS_TUPLE

### MODELO RELACIONAL (MR) ###
#
# usuario(@id, username, password, first_name, last_name, email, telefono, 
#         fecha_registro, fecha_ultima_modificacion, rol, email_verified)
# 
# cliente(id, id_usuario, direccion_hogar)
#   - FK: id_usuario -> usuario(id)
#
# conductor(id, id_usuario, estado, id_vehiculo)
#   - FK: id_usuario -> usuario(id)
#   - FK: id_vehiculo -> vehiculo(matricula)
# 
# admin(id, id_usuario, nivel_acceso)
#   - FK: id_usuario -> usuario(id)
#
# despachador(id, id_usuario)
#   - FK: id_usuario -> usuario(id)
#
# vehiculo(@matricula, marca, año_de_fabricacion)
#
# paquete(@id, largo, ancho, alto, peso, fecha_registro, fecha_entrega, estado,
#         ubicacion_actual_lat, ubicacion_actual_lng, ubicacion_actual_texto,
#         direccion_envio_lat, direccion_envio_lng, direccion_envio_texto,
#         nombre_destinatario, rut_destinatario, telefono_destinatario,
#         id_cliente, id_conductor, id_despachador)
#   - FK: id_cliente -> cliente(id)
#   - FK: id_conductor -> conductor(id)
#   - FK: id_despachador -> despachador(id)
#
# ruta(@id, tipo_ruta, ruta_ida_coordenadas, ruta_ida_polyline, distancia_ida_km,
#      duracion_ida_minutos, ruta_regreso_coordenadas, ruta_regreso_polyline,
#      distancia_regreso_km, duracion_regreso_minutos, distancia_total_km,
#      duracion_total_minutos, fecha_calculo, fecha_en_que_se_ejecuto,
#      origen_direccion, destino_direccion, origen_lat, origen_lng,
#      destino_lat, destino_lng, fecha_inicio_ruta, fecha_fin_ruta, id_paquete)
#   - FK: id_paquete -> paquete(id) [OneToOne]
#
# notificacion(@id, mensaje, fecha_envio, id_cliente, id_paquete)
#   - FK: id_cliente -> cliente(id)
#   - FK: id_paquete -> paquete(id)
#
### FIN MODELO RELACIONAL ###


# ========== ENUMERACIONES Y CHOICES ==========

class TiposRoles(models.TextChoices):
    """Tipos de roles disponibles en el sistema."""
    CLIENTE = 'cliente', 'Cliente'
    CONDUCTOR = 'conductor', 'Conductor'
    DESPACHADOR = 'despachador', 'Despachador'
    ADMIN = 'admin', 'Admin'

class EstadoConductor(models.TextChoices):
    """Estados posibles de un conductor."""
    EN_RUTA = 'en_ruta', 'En ruta'
    DISPONIBLE = 'disponible', 'Disponible'
    NO_DISPONIBLE = 'no disponible', 'No disponible'

class EstadoPaquete(models.TextChoices):
    """Estados del ciclo de vida de un paquete."""
    EN_BODEGA = 'en_bodega', 'En bodega'
    EN_RUTA = 'en_ruta', 'En ruta'
    ENTREGADO = 'entregado', 'Entregado'

class TipoRuta(models.TextChoices):
    """Tipos de ruta según su dirección."""
    IDA = 'ida', 'Ruta de Ida'
    REGRESO = 'regreso', 'Ruta de Regreso'
    COMPLETA = 'completa', 'Ruta Completa (Ida y Regreso)'


# ========== MODELOS DE USUARIOS ==========

class Usuario(AbstractUser):
    """
    Modelo base de usuario extendido de AbstractUser.
    
    Representa a todos los usuarios del sistema con diferentes roles.
    Hereda username, password, email, first_name, last_name de AbstractUser.
    """
    rol = models.CharField(
        max_length=100,
        choices=TiposRoles.choices,
        help_text="Rol del usuario en el sistema"
    )
    telefono = PhoneNumberField(
        blank=True, 
        null=True,
        help_text="Número de teléfono del usuario"
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de registro del usuario"
    )
    fecha_ultima_modificacion = models.DateTimeField(
        auto_now=True,
        help_text="Fecha y hora de la última modificación"
    )
    email_verified = models.BooleanField(
        default=False, 
        verbose_name="Correo verificado",
        help_text="Indica si el correo electrónico ha sido verificado"
    )

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"


class Cliente(models.Model):
    """
    Modelo que extiende Usuario para clientes del sistema.
    
    Los clientes pueden enviar paquetes y recibir notificaciones.
    """
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE,
        help_text="Usuario asociado al cliente"
    )
    direccion_hogar = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Dirección del hogar del cliente"
    )

    def __str__(self):
        return f"Cliente: {self.usuario.get_full_name()}"


class Conductor(models.Model):
    """
    Modelo que extiende Usuario para conductores del sistema.
    
    Los conductores se encargan de entregar los paquetes.
    """
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE,
        help_text="Usuario asociado al conductor"
    )
    estado = models.CharField(
        max_length=100,
        choices=EstadoConductor.choices,
        default=EstadoConductor.DISPONIBLE,
        help_text="Estado actual del conductor"
    )
    vehiculo = models.ForeignKey(
        'Vehiculo', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Vehículo asignado al conductor"
    )

    def __str__(self):
        return f"Conductor: {self.usuario.get_full_name()} ({self.get_estado_display()})"


class Despachador(models.Model):
    """
    Modelo que extiende Usuario para despachadores del sistema.
    
    Los despachadores gestionan la asignación de paquetes a conductores.
    """
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE,
        help_text="Usuario asociado al despachador"
    )

    def __str__(self):
        return f"Despachador: {self.usuario.get_full_name()}"


class Admin(models.Model):
    """
    Modelo que extiende Usuario para administradores del sistema.
    
    Los administradores tienen acceso completo al sistema.
    """
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE,
        help_text="Usuario asociado al administrador"
    )
    nivel_acceso = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        default=1,
        help_text="Nivel de acceso del administrador (1-5)"
    )

    def __str__(self):
        return f"Admin: {self.usuario.get_full_name()} (Nivel {self.nivel_acceso})"


# ========== MODELOS DE RECURSOS ==========

class Vehiculo(models.Model):
    """
    Modelo que representa los vehículos utilizados para entregas.
    """
    matricula = models.CharField(
        max_length=50, 
        primary_key=True,
        help_text="Matrícula única del vehículo"
    )
    marca = models.CharField(
        max_length=100,
        help_text="Marca del vehículo"
    )
    año_de_fabricacion = models.PositiveIntegerField(
        help_text="Año de fabricación del vehículo"
    )

    def __str__(self):
        return f"{self.marca} - {self.matricula} ({self.año_de_fabricacion})"

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"


# ========== MODELOS DE PAQUETES Y RUTAS ==========

class Paquete(models.Model):
    """
    Modelo que representa un paquete a entregar.
    
    Contiene toda la información necesaria para el envío, incluyendo
    dimensiones, ubicaciones, destinatario y estado actual.
    """
    id = models.AutoField(primary_key=True)

    # Dimensiones físicas del paquete
    largo = models.FloatField(
        validators=[MinValueValidator(0.01, "El valor debe ser mayor a 0.")],
        help_text="Largo del paquete en centímetros"
    )
    ancho = models.FloatField(
        validators=[MinValueValidator(0.01, "El valor debe ser mayor a 0.")],
        help_text="Ancho del paquete en centímetros"
    )
    alto = models.FloatField(
        validators=[MinValueValidator(0.01, "El valor debe ser mayor a 0.")],
        help_text="Alto del paquete en centímetros"
    )
    peso = models.FloatField(
        validators=[MinValueValidator(0.01, "El valor debe ser mayor a 0.")],
        help_text="Peso del paquete en kilogramos"
    )

    # Fechas del ciclo de vida
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de registro del paquete"
    )
    fecha_entrega = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha y hora de entrega del paquete"
    )

    # Estado del paquete
    estado = models.CharField(
        max_length=10,
        choices=EstadoPaquete.choices,
        default=EstadoPaquete.EN_BODEGA,
        help_text="Estado actual del paquete"
    )

    # Ubicación actual del paquete
    ubicacion_actual_lat = models.FloatField(
        default=UNIVERSIDAD_CONCEPCION_COORDS_TUPLE[0],
        help_text="Latitud de la ubicación actual"
    )
    ubicacion_actual_lng = models.FloatField(
        default=UNIVERSIDAD_CONCEPCION_COORDS_TUPLE[1],
        help_text="Longitud de la ubicación actual"
    )
    ubicacion_actual_texto = models.CharField(
        max_length=200,
        default=UNIVERSIDAD_CONCEPCION["direccion"],
        help_text="Descripción textual de la ubicación actual"
    )

    # Dirección de envío (destino)
    direccion_envio_lat = models.FloatField(
        help_text="Latitud de la dirección de envío"
    )
    direccion_envio_lng = models.FloatField(
        help_text="Longitud de la dirección de envío"
    )
    direccion_envio_texto = models.CharField(
        max_length=200,
        help_text="Descripción textual de la dirección de envío"
    )

    # Información del destinatario
    nombre_destinatario = models.CharField(
        max_length=255,
        help_text="Nombre completo del destinatario"
    )
    rut_destinatario = models.CharField(
        max_length=12,
        help_text="RUT del destinatario (formato: 12.345.678-9)"
    )
    telefono_destinatario = PhoneNumberField(
        help_text="Teléfono de contacto del destinatario"
    )

    # Relaciones con otros modelos
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name='paquetes',
        help_text="Cliente que envía el paquete"
    )
    conductor = models.ForeignKey(
        Conductor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='paquetes',
        help_text="Conductor asignado para la entrega"
    )
    despachador = models.ForeignKey(
        'Despachador', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='paquetes',
        help_text="Despachador que gestionó el paquete"
    )

    def __str__(self):
        return f"Paquete #{self.id} - {self.nombre_destinatario} ({self.get_estado_display()})"

    @property
    def volumen_cm3(self):
        """Calcula el volumen del paquete en centímetros cúbicos."""
        return self.largo * self.ancho * self.alto

    class Meta:
        verbose_name = "Paquete"
        verbose_name_plural = "Paquetes"

class Ruta(models.Model):
    """
    Modelo que almacena rutas de ida y regreso calculadas para paquetes.
    Optimizado para almacenar tanto coordenadas como polylines comprimidos.
    """
    id = models.AutoField(primary_key=True)
    tipo_ruta = models.CharField(max_length=10, choices=TipoRuta.choices, default=TipoRuta.COMPLETA)
    
    # Datos de la ruta de ida
    ruta_ida_coordenadas = models.JSONField(help_text="Coordenadas de la ruta de ida como lista de [lat, lng]")
    ruta_ida_polyline = models.TextField(help_text="Polyline codificado de la ruta de ida")
    distancia_ida_km = models.FloatField(help_text="Distancia de la ruta de ida en kilómetros")
    duracion_ida_minutos = models.PositiveIntegerField(help_text="Duración estimada de la ruta de ida en minutos")
    
    # Datos de la ruta de regreso
    ruta_regreso_coordenadas = models.JSONField(help_text="Coordenadas de la ruta de regreso como lista de [lat, lng]")
    ruta_regreso_polyline = models.TextField(help_text="Polyline codificado de la ruta de regreso")
    distancia_regreso_km = models.FloatField(help_text="Distancia de la ruta de regreso en kilómetros")
    duracion_regreso_minutos = models.PositiveIntegerField(help_text="Duración estimada de la ruta de regreso en minutos")
    
    # Totales calculados automáticamente
    distancia_total_km = models.FloatField(help_text="Distancia total (ida + regreso) en kilómetros")
    duracion_total_minutos = models.PositiveIntegerField(help_text="Duración total estimada (ida + regreso) en minutos")
    
    # Metadatos de la ruta
    fecha_calculo = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora cuando se calculó la ruta")
    origen_direccion = models.CharField(max_length=500, help_text="Dirección de origen (Universidad)")
    destino_direccion = models.CharField(max_length=500, help_text="Dirección de destino del paquete")
    
    # Coordenadas exactas de origen y destino
    origen_lat = models.FloatField(help_text="Latitud del punto de origen")
    origen_lng = models.FloatField(help_text="Longitud del punto de origen")
    destino_lat = models.FloatField(help_text="Latitud del punto de destino")
    destino_lng = models.FloatField(help_text="Longitud del punto de destino")
    
    # Relación uno a uno con paquete
    paquete = models.OneToOneField('Paquete', on_delete=models.CASCADE, related_name='ruta')
    
    fecha_inicio_ruta = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Fecha y hora cuando el conductor inició la ruta"
    )
    
    fecha_fin_ruta = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Fecha y hora cuando el conductor completó la ruta"
    )
    
    @property
    def duracion_real_minutos(self):
        """
        Calcula la duración real en minutos basada en las fechas de inicio y fin.
        Retorna None si no se han registrado ambas fechas.
        """
        if self.fecha_inicio_ruta and self.fecha_fin_ruta:
            delta = self.fecha_fin_ruta - self.fecha_inicio_ruta
            return int(delta.total_seconds() / 60)
        return None
    
    class Meta:
        verbose_name = "Ruta"
        verbose_name_plural = "Rutas"
    
    def __str__(self):
        return f"Ruta {self.paquete.id}: {self.origen_direccion} → {self.destino_direccion}"
    
    def save(self, *args, **kwargs):
        """Calcula automáticamente los totales antes de guardar"""
        self.distancia_total_km = self.distancia_ida_km + self.distancia_regreso_km
        self.duracion_total_minutos = self.duracion_ida_minutos + self.duracion_regreso_minutos
        super().save(*args, **kwargs)

# ========== MODELOS DE INFORMACION PARA USUARIOS ==========
class Notificacion(models.Model):
    """
    Modelo que representa notificaciones enviadas a clientes.
    
    Las notificaciones mantienen informados a los clientes sobre
    el estado de sus paquetes.
    """
    mensaje = models.TextField(
        help_text="Contenido del mensaje de la notificación"
    )
    fecha_envio = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de envío de la notificación"
    )
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name='notificaciones',
        help_text="Cliente que recibe la notificación"
    )
    paquete = models.ForeignKey(
        Paquete, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='notificaciones',
        help_text="Paquete relacionado con la notificación"
    )

    def __str__(self):
        return f"Notificación para {self.cliente.usuario.get_full_name()} - {self.fecha_envio.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha_envio']
