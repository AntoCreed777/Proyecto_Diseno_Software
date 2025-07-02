# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from maps.constants import UNIVERSIDAD_CONCEPCION, UNIVERSIDAD_CONCEPCION_COORDS_TUPLE

### Modelo MR
#
# usuario(@id, password, nombre, apellido, email, telefono, fecha_registro, fecha_ultima_modificacion, rol)
# 
# cliente(id_usuario, direccion_hogar)
#   - FK: id_usuario -> usuario(id)
#
# conductor(id_usuario, estado, id_vehiculo, id_despachador)
#   - FK: id_usuario -> usuario(id)
#   - FK: id_vehiculo -> vehiculo(id)
# 
# admin(id_usuario, nivel_acceso)
#   - FK: id_usuario -> usuario(id)
#
# despachador(id_usuario)
#   - FK: id_usuario -> usuario(id)
#
# ruta(@id, ruta_kml, duracion_estimada_minutos, distancia_km, fecha_en_que_se_ejecuto, id_paquete)
#   - FK: id_paquete -> paquete(id)
#
# vehiculo(@matricula, marca, año_de_fabricacion)
#
# paquete(@id, dimensiones, peso, fecha_registro, fecha_entrega, estado, ubicacion_actual, direccion_envio, nombre_destinatario, rut_destinatario, telefono_destinatario, id_cliente, id_conductor, id_despachador)
#   - FK: id_cliente -> cliente(id)
#   - FK: id_conductor -> conductor(id)
#   - FK: id_despachador -> despachador(id)
#
# notificacion(@id, mensaje, fecha_envio, id_cliente, id_paquete)
#   - FK: id_cliente -> cliente(id)
#   - FK: id_paquete -> paquete(id)
#
### Fin Modelo MR


class TiposRoles(models.TextChoices):
    CLIENTE = 'cliente', 'Cliente'
    CONDUCTOR = 'conductor', 'Conductor'
    DESPACHADOR = 'despachador', 'Despachador'
    ADMIN = 'admin', 'Admin'

# Modelo base de usuario (Es la generalizacion del MER)

class Usuario(AbstractUser):
    # username, password, email, first_name, last_name ya existen
    rol = models.CharField(
        max_length=100,
        choices=TiposRoles.choices
    )
    telefono = PhoneNumberField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)
    email_verified = models.BooleanField(default=False, verbose_name="Correo verificado")

class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    direccion_hogar = models.CharField(max_length=255, blank=True, null=True)

class EstadoConductor(models.TextChoices):
    EN_RUTA = 'en_ruta', 'En ruta'
    DISPONIBLE = 'disponible', 'Disponible'
    NO_DISPONIBLE = 'no disponible', 'No disponible'

class Conductor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    estado = models.CharField(
        max_length=100,
        choices=EstadoConductor.choices,
        default=EstadoConductor.DISPONIBLE
    )
    vehiculo = models.ForeignKey('Vehiculo', on_delete=models.SET_NULL, null=True, blank=True)

class Despachador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

class Admin(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nivel_acceso = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        default=1
    )

class Vehiculo(models.Model):
    matricula = models.CharField(max_length=50, primary_key=True)
    marca = models.CharField(max_length=100)
    año_de_fabricacion = models.PositiveIntegerField()

class EstadoPaquete(models.TextChoices):
    EN_BODEGA = 'en_bodega', 'En bodega'
    EN_RUTA = 'en_ruta', 'En ruta'
    ENTREGADO = 'entregado', 'Entregado'

class Paquete(models.Model):
    id = models.AutoField(primary_key=True)

    # Dimensiones
    largo = models.FloatField(validators=[MinValueValidator(0.01, "El valor debe ser mayor a 0.")])
    ancho = models.FloatField(validators=[MinValueValidator(0.01, "El valor debe ser mayor a 0.")])
    alto = models.FloatField(validators=[MinValueValidator(0.01, "El valor debe ser mayor a 0.")])

    peso = models.FloatField(validators=[MinValueValidator(0.01, "El valor debe ser mayor a 0.")])
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)

    estado = models.CharField(
        max_length=10,
        choices=EstadoPaquete.choices,
        default=EstadoPaquete.EN_BODEGA
    )

    # Ubicacion actual
    ubicacion_actual_lat = models.FloatField(default=UNIVERSIDAD_CONCEPCION_COORDS_TUPLE[0])
    ubicacion_actual_lng = models.FloatField(default=UNIVERSIDAD_CONCEPCION_COORDS_TUPLE[1])
    ubicacion_actual_texto =  models.CharField(
        max_length=200,
        default=UNIVERSIDAD_CONCEPCION["direccion"]
    )

    # Direccion envio
    direccion_envio_lat = models.FloatField()
    direccion_envio_lng = models.FloatField()
    direccion_envio_texto = models.CharField(max_length=200)

    nombre_destinatario = models.CharField(max_length=255)
    rut_destinatario = models.CharField(max_length=20)
    telefono_destinatario = PhoneNumberField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='paquetes')
    conductor = models.ForeignKey(Conductor, on_delete=models.SET_NULL, null=True, blank=True, related_name='paquetes')
    despachador = models.ForeignKey('Despachador', on_delete=models.SET_NULL, null=True, blank=True, related_name='paquetes')

class Notificacion(models.Model):
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='notificaciones')
    paquete = models.ForeignKey(Paquete, on_delete=models.SET_NULL, null=True, blank=True, related_name='notificaciones')

class TipoRuta(models.TextChoices):
    IDA = 'ida', 'Ruta de Ida'
    REGRESO = 'regreso', 'Ruta de Regreso'
    COMPLETA = 'completa', 'Ruta Completa (Ida y Regreso)'

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
    fecha_en_que_se_ejecuto = models.DateTimeField(null=True, blank=True, help_text="Fecha y hora cuando se ejecutó la ruta")
    origen_direccion = models.CharField(max_length=500, help_text="Dirección de origen (Universidad)")
    destino_direccion = models.CharField(max_length=500, help_text="Dirección de destino del paquete")
    
    # Coordenadas exactas de origen y destino
    origen_lat = models.FloatField(help_text="Latitud del punto de origen")
    origen_lng = models.FloatField(help_text="Longitud del punto de origen")
    destino_lat = models.FloatField(help_text="Latitud del punto de destino")
    destino_lng = models.FloatField(help_text="Longitud del punto de destino")
    
    # Relación uno a uno con paquete
    paquete = models.OneToOneField('Paquete', on_delete=models.CASCADE, related_name='ruta')
    
    # Duración real (registrada por el conductor)
    duracion_real_minutos = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Duración real que tomó al conductor completar la ruta (en minutos)"
    )
    
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
