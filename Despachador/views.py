from django.http import HttpResponse
from django.template import Template, Context
from django.template import loader
from django.shortcuts import render, redirect
from api.models import Paquete, Cliente, Usuario, Despachador, Conductor
from api.serializers import UsuarioSerializer, PaqueteSerializer, ClienteSerializer
from rest_framework.exceptions import ValidationError
from django.contrib import messages

def inicio(request):

    return render(request,'despachador/inicio.html')

def paquetes(request):
    clientes = Cliente.objects.select_related('usuario').all()
    paquetes = Paquete.objects.all().order_by('-id')
    conductores = Conductor.objects.all()
    return render(request,'despachador/paquetes.html', {
        'clientes': clientes,
        'paquetes': paquetes,
        })

def conductores(request):
    conductores = Conductor.objects.all()
    return render(request,'despachador/conductores.html',{'conductores': conductores})

def registrar_paquete(request):
    if request.method == 'POST':
        data = {
            'dimensiones': request.POST.get('dimensiones'),
            'peso': request.POST.get('peso'),
            'ubicacion_actual_lat': 0.0,
            'ubicacion_actual_lng': 0.0,
            'direccion_envio_lat': 0.0,
            'direccion_envio_lng': 0.0,
            'nombre_destinatario': request.POST.get('nombre_destinatario'),
            'rut_destinatario': request.POST.get('rut_destinatario'),
            'telefono_destinatario': request.POST.get('telefono_destinatario'),
            'cliente': request.POST.get('cliente_id'),
            'despachador': Despachador.objects.get(usuario=request.user).id,
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
            # Agrega cada error del serializer a messages
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'despachador/paquetes.html', {
                'clientes': Cliente.objects.select_related('usuario').all(),
                'paquetes': Paquete.objects.all().order_by('-id'),
                'show_cliente_modal': True,
            })
    return redirect('paquetes_despachador')