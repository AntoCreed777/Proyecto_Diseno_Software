from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from api.models import (
    Usuario, Cliente, Conductor, Despachador, Admin, Vehiculo,
    Ruta, Paquete, Notificacion,
    TiposRoles
)

class Command(BaseCommand):
    help = 'Crear grupos y permisos iniciales'

    def handle(self, *args, **kwargs):
        # Crear grupos (una vez)
        cliente_group, _ = Group.objects.get_or_create(name=TiposRoles.CLIENTE)
        conductor_group, _ = Group.objects.get_or_create(name=TiposRoles.CONDUCTOR)
        despachador_group, _ = Group.objects.get_or_create(name=TiposRoles.DESPACHADOR)
        admin_group, _ = Group.objects.get_or_create(name=TiposRoles.ADMIN)

        def obtener_permisos(modelo):
            """
            Obtiene o crea permisos básicos para un modelo.
            Retorna un diccionario con los permisos.
            """
            content_type = ContentType.objects.get_for_model(modelo)

            permisos = {
                'add': Permission.objects.get_or_create(codename=f'add_{modelo._meta.model_name}', content_type=content_type)[0],
                'change': Permission.objects.get_or_create(codename=f'change_{modelo._meta.model_name}', content_type=content_type)[0],
                'delete': Permission.objects.get_or_create(codename=f'delete_{modelo._meta.model_name}', content_type=content_type)[0],
                'view': Permission.objects.get_or_create(codename=f'view_{modelo._meta.model_name}', content_type=content_type)[0],
            }
            return permisos

        # Obtener permisos para cada modelo
        permisos_usuario = obtener_permisos(Usuario)
        permisos_cliente = obtener_permisos(Cliente)
        permisos_conductor = obtener_permisos(Conductor)
        permisos_despachador = obtener_permisos(Despachador)
        permisos_admin = obtener_permisos(Admin)
        permisos_vehiculo = obtener_permisos(Vehiculo)
        permisos_ruta = obtener_permisos(Ruta)
        permisos_paquete = obtener_permisos(Paquete)
        permisos_notificacion = obtener_permisos(Notificacion)

        # Solo al admin le doy permisos sobre la BD, si se llegara a crear un nuevo grupo que necesita
        # interactuar directamente con la BD, aqui hay que otorgarle lo permisos correspondientes 

        # Admin puede tener todos los permisos
        admin_group.permissions.set(Permission.objects.all())

