from django.core.management.base import BaseCommand
from api.models import Usuario, Cliente, Conductor, Despachador, Admin, TiposRoles
from django.db import transaction
from phonenumber_field.phonenumber import PhoneNumber

class Command(BaseCommand):
    help = 'Poblar la base de Datos con datos de prueba'

    def handle(self, *args, **kwargs):
        # Crear Cliente
        try:
            with transaction.atomic():
                usuario_cliente = Usuario.objects.create_user(
                    username='cliente1',
                    email='cliente1@email.com',
                    first_name='Carlos',
                    last_name='Pérez',
                    password='cliente123',
                    rol=TiposRoles.CLIENTE,
                    telefono=PhoneNumber.from_string('+56911111111')
                )
                usuario_cliente.email_verified = True
                usuario_cliente.save()
                cliente = Cliente.objects.create(usuario=usuario_cliente, direccion_hogar='Calle Falsa 123, Ciudad')
                self.stdout.write(self.style.SUCCESS(f'Cliente creado: {usuario_cliente.username}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error al crear cliente: {e}'))

        # Crear Despachador
        try:
            with transaction.atomic():
                usuario_despachador = Usuario.objects.create_user(
                    username='despachador1',
                    email='despachador1@email.com',
                    first_name='Ana',
                    last_name='Gómez',
                    password='despachador123',
                    rol=TiposRoles.DESPACHADOR,
                    telefono=PhoneNumber.from_string('+56922222222')
                )
                usuario_despachador.email_verified = True
                usuario_despachador.save()
                despachador = Despachador.objects.create(usuario=usuario_despachador)
                self.stdout.write(self.style.SUCCESS(f'Despachador creado: {usuario_despachador.username}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error al crear despachador: {e}'))

        # Crear Conductor
        try:
            with transaction.atomic():
                usuario_conductor = Usuario.objects.create_user(
                    username='conductor1',
                    email='conductor1@email.com',
                    first_name='Luis',
                    last_name='Soto',
                    password='conductor123',
                    rol=TiposRoles.CONDUCTOR,
                    telefono=PhoneNumber.from_string('+56933333333')
                )
                usuario_conductor.email_verified = True
                usuario_conductor.save()
                conductor = Conductor.objects.create(usuario=usuario_conductor)
                self.stdout.write(self.style.SUCCESS(f'Conductor creado: {usuario_conductor.username}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error al crear conductor: {e}'))

        # Crear Admin
        try:
            with transaction.atomic():
                usuario_admin = Usuario.objects.create_user(
                    username='admin1',
                    email='admin1@email.com',
                    first_name='Sofia',
                    last_name='Martínez',
                    password='admin123',
                    rol=TiposRoles.ADMIN,
                    telefono=PhoneNumber.from_string('+56944444444')
                )
                usuario_admin.email_verified = True
                usuario_admin.save()
                admin = Admin.objects.create(usuario=usuario_admin, nivel_acceso=5)
                self.stdout.write(self.style.SUCCESS(f'Admin creado: {usuario_admin.username}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error al crear admin: {e}'))
