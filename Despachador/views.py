from django.http import HttpResponse
from django.template import Template, Context
from django.template import loader
from django.shortcuts import render, redirect
from api.models import Paquete, Cliente, Usuario, Despachador

def inicio(request):

    return render(request,'despachador/inicio.html')

def paquetes(request):
    clientes = Cliente.objects.select_related('usuario').all()
    paquetes = Paquete.objects.all().order_by('-id')
    return render(request,'despachador/paquetes.html', {
        'clientes': clientes,
        'paquetes': paquetes,
        })

def conductores(request):

    return render(request,'despachador/conductores.html')

def registrar_paquete(request):
    if request.method == 'POST':
        Paquete.objects.create(
            dimensiones= request.POST.get('dimensiones'),
            peso=request.POST.get('peso'),
            ubicacion_actual_lat=0.0,
            ubicacion_actual_lng=0.0,
            direccion_envio_lat=0.0,
            direccion_envio_lng=0.0,
            nombre_destinatario= request.POST.get('nombre_destinatario'),
            rut_destinatario= request.POST.get('rut_destinatario'),
            telefono_destinatario= request.POST.get('telefono_destinatario'),
            cliente_id=request.POST.get('cliente_id'),
            despachador_id=Despachador.objects.get(usuario=request.user).id,
        )
        return redirect('paquetes_despachador')
    return redirect('paquetes_despachador')
def registrar_cliente(request):
    if request.method == 'POST':
        usuario = Usuario.objects.create(
            username=request.POST.get('username'),
            first_name=request.POST.get('nombre'),
            last_name=request.POST.get('apellido'),
            email=request.POST.get('correo'),
            password=request.POST.get('contraseña'),
            telefono=request.POST.get('telefono'),
            rol='cliente'
        )
        Cliente.objects.create(
            usuario=usuario,
            direccion_hogar= request.POST.get('direccion')
        )
        return redirect('paquetes_despachador')
    return redirect('paquetes_despachador')
def detalles_paquete(request, paquete_id):

    return redirect('paquetes_despachador')