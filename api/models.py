# Create your models here.
from django.db import models


class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    correo = models.EmailField(unique=True)
    nombre = models.CharField(max_length=255)
    contraseña = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True # Esta clase no se crea como tabla en la base de datos


class Cliente(Usuario):
    pass


class Conductor(Usuario):
    pass


class Admin(Usuario):
    nivel_acceso = models.CharField(max_length=50)


class Vehiculo(models.Model):
    matricula = models.CharField(max_length=50, primary_key=True)
    marca = models.CharField(max_length=100)
    año_de_fabricacion = models.PositiveIntegerField()
    conductor = models.OneToOneField(Conductor, on_delete=models.SET_NULL, null=True, blank=True)


class Ruta(models.Model):
    id = models.AutoField(primary_key=True)
    ruta_kml = models.TextField()
    duracion_estimada_min = models.PositiveIntegerField()
    distancia_km = models.FloatField()
    origen = models.CharField(max_length=255)
    destino = models.CharField(max_length=255)


class Paquete(models.Model):
    id = models.AutoField(primary_key=True)
    ubicacion_actual = models.CharField(max_length=255)
    direccion_envio = models.CharField(max_length=255)
    dimensiones = models.CharField(max_length=100)
    peso = models.FloatField()


class EstadoEntrega(models.Model):
    id = models.AutoField(primary_key=True)
    estado = models.CharField(max_length=100)
    paquete = models.OneToOneField(Paquete, on_delete=models.CASCADE, related_name='estado')


class Notificacion(models.Model):
    id = models.AutoField(primary_key=True)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='notificaciones')


class Entrega(models.Model):
    id = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='entregas')
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE, related_name='entregas')
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE, related_name='entregas')
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='entregas')
    estado_entrega = models.ForeignKey(EstadoEntrega, on_delete=models.CASCADE, related_name='entregas')
