from django.db import models

# Create your models here.

class paquete(models.Model):
    id = models.IntegerField(primary_key = True)
    ubicacion_actual = models.CharField(max_length = 255)
    fecha_envio = models.DateField()
    direccion_envio = models.CharField(max_length = 255)
    dimensiones = models.FloatField()
    peso = models.FloatField()