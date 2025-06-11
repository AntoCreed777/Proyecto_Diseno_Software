from django.http import HttpResponse
from django.template import Template, Context
from django.template import loader
from django.shortcuts import render, redirect
from api.models import Paquete, Cliente, Usuario, Despachador, Conductor
from api.serializers import UsuarioSerializer, PaqueteSerializer, ClienteSerializer
from rest_framework.exceptions import ValidationError
from django.contrib import messages
from django.views.decorators.http import require_POST

def inicio(request):

    return render(request,'despachador/inicio.html')

def paquetes(request):
    paquetes = Paquete.objects.all()
    id_paquete = request.GET.get('id')
    fecha = request.GET.get('fecha')
    estado = request.GET.get('estado')
    conductor = request.GET.get('conductor')

    if id_paquete:
        paquetes = paquetes.filter(id=id_paquete)
    if fecha:
        paquetes = paquetes.filter(fecha_registro__date=fecha)
    if estado:
        paquetes = paquetes.filter(estado__estado=estado)
    if conductor:
        paquetes = paquetes.filter(conductor__id=conductor)

    clientes = Cliente.objects.select_related('usuario').all()
    conductores = Conductor.objects.select_related('usuario').all()
    return render(request, 'despachador/paquetes.html', {
        'clientes': clientes,
        'paquetes': paquetes.order_by('-id'),
        'conductores': conductores,
    })

def conductores(request):
    conductores = Conductor.objects.select_related('usuario', 'vehiculo').all()
    id_conductor = request.GET.get('id')
    nombre = request.GET.get('nombre')
    estado = request.GET.get('estado')
    vehiculo = request.GET.get('vehiculo')

    if id_conductor:
        conductores = conductores.filter(id=id_conductor)
    if nombre:
        conductores = conductores.filter(
            usuario__first_name__icontains=nombre
        )
    if estado:
        conductores = conductores.filter(estado=estado)
    if vehiculo:
        conductores = conductores.filter(vehiculo__matricula__icontains=vehiculo)

    return render(request, 'despachador/conductores.html', {'conductores': conductores})

def registrar_paquete(request):
    if request.method == 'POST':
        data = {
            'dimensiones': request.POST.get('dimensiones'),
            'peso': request.POST.get('peso'),
            'ubicacion_actual_lat': 0.0,
            'ubicacion_actual_lng': 0.0,
            'ubicacion_actual_texto': 'En Bodega',
            'direccion_envio_lat': 0.0,
            'direccion_envio_lng': 0.0,
            'direccion_envio_texto': request.POST.get('direccion_envio_texto'),
            'nombre_destinatario': request.POST.get('nombre_destinatario'),
            'rut_destinatario': request.POST.get('rut_destinatario'),
            'telefono_destinatario': request.POST.get('telefono_destinatario'),
            'cliente': request.POST.get('cliente_id'),
            'despachador': Despachador.objects.get(usuario=request.user).id,
            'estado': 'en_bodega',
        }
        serializer = PaqueteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return redirect('paquetes_despachador')
        else:
            return render(request, 'despachador/paquetes.html', {
                'clientes': Cliente.objects.select_related('usuario').all(),
                'paquetes': Paquete.objects.all().order_by('-id'),
                'errors_paquete': serializer.errors,
                'show_paquete_modal': True,
            })
    return redirect('paquetes_despachador')

def registrar_cliente(request):
    if request.method == 'POST':
        usuario_data = {
            'username': request.POST.get('username'),
            'first_name': request.POST.get('nombre'),
            'last_name': request.POST.get('apellido'),
            'email': request.POST.get('correo'),
            'password': request.POST.get('contraseña'),
            'telefono': request.POST.get('telefono'),
        }
        cliente_data = {
            'usuario': usuario_data,
            'direccion_hogar': request.POST.get('direccion')
        }
        serializer = ClienteSerializer(data=cliente_data)
        if serializer.is_valid():
            serializer.save()
        else:
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'despachador/paquetes.html', {
                'clientes': Cliente.objects.select_related('usuario').all(),
                'paquetes': Paquete.objects.all().order_by('-id'),
                'show_cliente_modal': True,
            })
    return redirect('paquetes_despachador')

def asignar_conductor(request):
    if request.method == 'POST':
        paquete_id = request.POST.get('paquete_id')
        conductor_id = request.POST.get('conductor_id')
        paquete = Paquete.objects.get(id=paquete_id)
        conductor = Conductor.objects.get(id=conductor_id)
        paquete.conductor = conductor
        paquete.save()
    return redirect('paquetes_despachador')

def cambiar_estado_paquete(request):
    if request.method == 'POST':
        paquete_id = request.POST.get('paquete_id')
        paquete = Paquete.objects.get(id=paquete_id)
        paquete.estado = request.POST.get('estado')
        paquete.save()
    return redirect('paquetes_despachador')