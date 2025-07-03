from django.http import HttpResponse
from django.template import Template, Context
from django.template import loader
from django.shortcuts import render, redirect
from api.models import Paquete, Cliente, Usuario, Despachador, Conductor
from django.contrib import messages
from django.views.decorators.http import require_POST
from accounts.views import notificar_cambio_estado_paquete

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
        paquetes = paquetes.filter(estado=estado)
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
        from .forms import RegistroPaqueteForm
        
        form = RegistroPaqueteForm(request.POST)
        if form.is_valid():
            try:
                despachador = Despachador.objects.get(usuario=request.user)
                paquete = form.save(commit=True, despachador=despachador)
                messages.success(request, 'Paquete registrado exitosamente.')
                return redirect('paquetes_despachador')
            except Exception as e:
                messages.error(request, f'Error al registrar el paquete: {str(e)}')
                return render(request, 'despachador/registrar_paquete.html', {'form': form})
        else:
            return render(request, 'despachador/registrar_paquete.html', {'form': form})
    else:
        from .forms import RegistroPaqueteForm
        form = RegistroPaqueteForm()
        return render(request, 'despachador/registrar_paquete.html', {'form': form})

def registrar_cliente(request):
    if request.method == 'POST':
        from accounts.forms import RegistroClienteForm
        from accounts.views import activarEmail
        
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=True)
            activarEmail(request, usuario)
            messages.success(request, 'Cliente registrado exitosamente. Se ha enviado un correo de verificación.')
            return redirect('paquetes_despachador')
        else:
            return render(request, 'despachador/registrar_cliente.html', {'form': form})
    else:
        from accounts.forms import RegistroClienteForm
        form = RegistroClienteForm()
        return render(request, 'despachador/registrar_cliente.html', {'form': form})

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
        notificar_cambio_estado_paquete(paquete)
    return redirect('paquetes_despachador')