"""
Comando Django para poblar la base de datos con usuarios de prueba.

Uso:
    python manage.py poblar_bd

Crea usuarios de prueba para cada rol del sistema:
- Cliente (cliente1)
- Despachador (despachador1) 
- Conductor (conductor1)
- Admin (admin1)

Nota: El comando verifica si los usuarios ya existen antes de crearlos.
"""

from django.core.management.base import BaseCommand
from api.models import Usuario, Cliente, Conductor, Despachador, Admin, TiposRoles
from django.db import transaction
from phonenumber_field.phonenumber import PhoneNumber
from django.contrib.auth.models import Group
from api.exceptions import GroupNotConfiguredError

class Command(BaseCommand):
    help = 'Poblar la base de datos con usuarios de prueba para cada rol del sistema'

    def handle(self, *args, **kwargs):
        """Ejecuta la creación de usuarios de prueba."""
        # Crear Cliente de prueba
        try:
            with transaction.atomic():
                if Usuario.objects.filter(username='cliente1').exists():
                    self.stdout.write(self.style.WARNING('Cliente1 ya existe, saltando...'))
                else:
                    usuario_cliente = Usuario.objects.create_user(
                        username='cliente1',
                        email='cliente1@email.com',
                        first_name='Carlos',
                        last_name='Pérez',
                        rol=TiposRoles.CLIENTE,
                        telefono=PhoneNumber.from_string('+56911111111')
                    )
                    usuario_cliente.set_password('cliente123')  # Hashea la contraseña
                    usuario_cliente.email_verified = True
                    usuario_cliente.save()
                    
                    # Asignar grupo correspondiente al rol
                    try:
                        grupo = Group.objects.get(name=TiposRoles.CLIENTE)
                        usuario_cliente.groups.add(grupo)
                    except Group.DoesNotExist:
                        raise GroupNotConfiguredError(f"El grupo '{TiposRoles.CLIENTE}' no está configurado en la base de datos.")
                    
                    cliente = Cliente.objects.create(usuario=usuario_cliente, direccion_hogar='Calle Falsa 123, Ciudad')
                    self.stdout.write(self.style.SUCCESS(f'Cliente creado: {usuario_cliente.username}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error al crear cliente: {e}'))

        # Crear Despachador de prueba
        try:
            with transaction.atomic():
                if Usuario.objects.filter(username='despachador1').exists():
                    self.stdout.write(self.style.WARNING('Despachador1 ya existe, saltando...'))
                else:
                    usuario_despachador = Usuario.objects.create_user(
                        username='despachador1',
                        email='despachador1@email.com',
                        first_name='Ana',
                        last_name='Gómez',
                        rol=TiposRoles.DESPACHADOR,
                        telefono=PhoneNumber.from_string('+56922222222')
                    )
                    usuario_despachador.set_password('despachador123')
                    usuario_despachador.email_verified = True
                    usuario_despachador.save()
                    
                    # Asignar grupo correspondiente al rol
                    try:
                        grupo = Group.objects.get(name=TiposRoles.DESPACHADOR)
                        usuario_despachador.groups.add(grupo)
                    except Group.DoesNotExist:
                        raise GroupNotConfiguredError(f"El grupo '{TiposRoles.DESPACHADOR}' no está configurado en la base de datos.")
                    
                    despachador = Despachador.objects.create(usuario=usuario_despachador)
                    self.stdout.write(self.style.SUCCESS(f'Despachador creado: {usuario_despachador.username}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error al crear despachador: {e}'))

        # Crear Conductor de prueba
        try:
            with transaction.atomic():
                if Usuario.objects.filter(username='conductor1').exists():
                    self.stdout.write(self.style.WARNING('Conductor1 ya existe, saltando...'))
                else:
                    usuario_conductor = Usuario.objects.create_user(
                        username='conductor1',
                        email='conductor1@email.com',
                        first_name='Luis',
                        last_name='Soto',
                        rol=TiposRoles.CONDUCTOR,
                        telefono=PhoneNumber.from_string('+56933333333')
                    )
                    usuario_conductor.set_password('conductor123')
                    usuario_conductor.email_verified = True
                    usuario_conductor.save()
                    
                    # Asignar grupo correspondiente al rol
                    try:
                        grupo = Group.objects.get(name=TiposRoles.CONDUCTOR)
                        usuario_conductor.groups.add(grupo)
                    except Group.DoesNotExist:
                        raise GroupNotConfiguredError(f"El grupo '{TiposRoles.CONDUCTOR}' no está configurado en la base de datos.")
                    
                    conductor = Conductor.objects.create(usuario=usuario_conductor)
                    self.stdout.write(self.style.SUCCESS(f'Conductor creado: {usuario_conductor.username}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error al crear conductor: {e}'))

        # Crear Admin de prueba (superusuario)
        try:
            with transaction.atomic():
                if Usuario.objects.filter(username='admin1').exists():
                    self.stdout.write(self.style.WARNING('Admin1 ya existe, saltando...'))
                else:
                    usuario_admin = Usuario.objects.create_superuser(
                        username='admin1',
                        email='admin1@email.com',
                        first_name='Sofia',
                        last_name='Martínez',
                        password='admin123',    # create_superuser() hashea automáticamente
                        rol=TiposRoles.ADMIN,
                        telefono=PhoneNumber.from_string('+56944444444')
                    )
                    usuario_admin.email_verified = True
                    usuario_admin.save()
                    
                    # Asignar grupo correspondiente al rol
                    try:
                        grupo = Group.objects.get(name=TiposRoles.ADMIN)
                        usuario_admin.groups.add(grupo)
                    except Group.DoesNotExist:
                        raise GroupNotConfiguredError(f"El grupo '{TiposRoles.ADMIN}' no está configurado en la base de datos.")
                    
                    admin = Admin.objects.create(usuario=usuario_admin, nivel_acceso=5)
                    self.stdout.write(self.style.SUCCESS(f'Admin creado: {usuario_admin.username}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error al crear admin: {e}'))
