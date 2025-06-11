# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField

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
# ruta(@id, ruta_kml, duracion_estimada_minutos, distancia_km, origen, destino, fecha_en_que_se_ejecuto)
#
# conductorPOSEEruta(id_conductor, id_ruta)
#   - FK: id_conductor -> conductor(id)
#   - FK: id_ruta -> ruta(id)
#
# vehiculo(@matricula, marca, año_de_fabricacion)
#
# paquete(@id, dimensiones, peso, fecha_registro, fecha_entrega, ubicacion_actual, direccion_envio, nombre_destinatario, rut_destinatario, telefono_destinatario, id_cliente, id_conductor, id_estado, id_despachador)
#   - FK: id_cliente -> cliente(id)
#   - FK: id_conductor -> conductor(id)
#   - FK: id_estado -> estado(id)
#   - FK: id_despachador -> despachador(id)
#
# estado_entrega(@id, estado)
#
# notificacion(@id, mensaje, fecha_envio, id_cliente)
#   - FK: id_cliente -> cliente(id)
#
### Fin Modelo MR


# Modelo base de usuario (Es la generalizacion del MER)
class Usuario(AbstractUser):
    # username, password, email, first_name, last_name ya existen
    rol = models.CharField(max_length=20, choices=[('cliente', 'Cliente'), ('conductor', 'Conductor'), ('admin', 'Admin'), ('despachador', 'Despachador')])
    telefono = PhoneNumberField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)
    email_verified = models.BooleanField(default=False, verbose_name="Correo verificado")

class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    direccion_hogar = models.CharField(max_length=255, blank=True, null=True)

class Conductor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=[('en_ruta', 'En_Ruta'), ('disponible', 'Disponible'), ('no disponible', 'No Disponible')])
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

class Ruta(models.Model):
    id = models.AutoField(primary_key=True)
    ruta_kml = models.TextField()
    duracion_estimada_minutos = models.PositiveIntegerField()
    distancia_km = models.FloatField()
    origen = models.CharField(max_length=255)
    destino = models.CharField(max_length=255)
    fecha_en_que_se_ejecuto = models.DateTimeField(null=True, blank=True)

# Relación muchos a muchos entre Conductor y Ruta
class ConductorPoseeRuta(models.Model):
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE)
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)

class Paquete(models.Model):
    id = models.AutoField(primary_key=True)
    dimensiones = models.CharField(max_length=100)
    peso = models.FloatField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField(auto_now_add=True)

    estado = models.CharField(max_length=100, choices=[('en_bodega', 'En_Bodega'), ('en_ruta', 'En_ruta'), ('entregado', 'Entregado')])

    # Ubicacion actual
    ubicacion_actual_lat = models.FloatField()
    ubicacion_actual_lng = models.FloatField()
    ubicacion_actual_texto =  models.CharField(max_length=200)

    # Direccion envio
    direccion_envio_lat = models.FloatField()
    direccion_envio_lng = models.FloatField()
    direccion_envio_texto = models.CharField(max_length=200)

    nombre_destinatario = models.CharField(max_length=255)
    rut_destinatario = models.CharField(max_length=20)
    telefono_destinatario = models.CharField(max_length=20)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='paquetes')
    conductor = models.ForeignKey(Conductor, on_delete=models.SET_NULL, null=True, blank=True, related_name='paquetes')
    despachador = models.ForeignKey('Despachador', on_delete=models.SET_NULL, null=True, blank=True, related_name='paquetes')

class Notificacion(models.Model):
    id = models.AutoField(primary_key=True)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='notificaciones')
