from django.http import HttpResponse
from django.template import Template, Context
from django.template import loader
from django.shortcuts import render, redirect
from django.utils import timezone
from api.models import ConductorPoseeRuta, Paquete, Notificacion, Cliente, Conductor, Ruta
from api.serializers import NotificacionSerializer
from datetime import datetime, timedelta 
from django.db.models import Q, Avg, Sum, Count
from accounts.views import notificar_cambio_estado_paquete


def inicio(request):
    #conductor = Conductor.objects.get(usuario=request.user)             #DEPENDE DE ESTAR LOGEADO, ESTE DEBERÍA USARSE
    conductor = getattr(request.user, 'conductor', None)#DEPENDE DE ESTAR LOGEADO, SOLO PARA VER LA INTERFAZ
    paquetes = Paquete.objects.filter(conductor=conductor)#DEPENDE DE ESTAR LOGEADO

    id_paquete = request.GET.get('id')
    fecha = request.GET.get('fecha')
    estado = request.GET.get('estado')

    if id_paquete:
        paquetes = paquetes.filter(id=id_paquete)
    if fecha:
        paquetes = paquetes.filter(fecha_registro__date=fecha)
    if estado:
        paquetes = paquetes.filter(estado=estado)

    rutas_asignadas = ConductorPoseeRuta.objects.filter(conductor=conductor).count()#DEPENDE DE ESTAR LOGEADO
    paquetes_pendientes = paquetes.filter(estado='en_bodega').count()
    paquetes_en_curso = paquetes.filter(estado='en_ruta').count()
    paquetes_entregados = paquetes.filter(estado='entregado').count()
    

    total_paquetes_asignados = paquetes.count()
    rendimiento = (paquetes_entregados/total_paquetes_asignados * 100) if total_paquetes_asignados > 0 else 0
    clientes = Cliente.objects.select_related('usuario').all()
    
    return render(request, 'Conductor/inicio.html', {
        'clientes': clientes,
        'paquetes': paquetes.order_by('-id'),
        'rutas_asignadas': rutas_asignadas,
        'paquetes_pendientes': paquetes_pendientes,
        'paquetes_en_curso': paquetes_en_curso,
        'paquetes_entregados': paquetes_entregados,
        'rendimiento': round(rendimiento, 2),
    })

def paquetes(request):
    #conductor = Conductor.objects.get(usuario=request.user)             #DEPENDE DE ESTAR LOGEADO, ESTE DEBERÍA USARSE
    conductor = getattr(request.user, 'conductor', None)#DEPENDE DE ESTAR LOGEADO, SOLO PARA VER LA INTERFAZ
    paquetes = Paquete.objects.filter(conductor=conductor)
    
    id_paquete = request.GET.get('id')
    fecha = request.GET.get('fecha')
    estado = request.GET.get('estado')
    clientes = Cliente.objects.select_related('usuario').all()
    conductores = Conductor.objects.select_related('usuario').all()

    if id_paquete:
        paquetes = paquetes.filter(id=id_paquete)
    if fecha:
        paquetes = paquetes.filter(fecha_registro__date=fecha)
    if estado:
        paquetes = paquetes.filter(estado=estado)

    return render(request, 'Conductor/paquetes.html', {
        'clientes': clientes,
        'paquetes': paquetes.order_by('-id'),
        'conductores':conductores,
    })

def rendimiento(request):
    #conductor = Conductor.objects.get(usuario=request.user)             #DEPENDE DE ESTAR LOGEADO, ESTE DEBERÍA USARSE
    conductor = getattr(request.user, 'conductor', None)#DEPENDE DE ESTAR LOGEADO, SOLO PARA VER LA INTERFAZ
    paquetes = Paquete.objects.filter(conductor=conductor)
    
    id_paquete = request.GET.get('id')
    fecha = request.GET.get('fecha')
    estado = request.GET.get('estado')

    if id_paquete:
        paquetes = paquetes.filter(id=id_paquete)
    if fecha:
        paquetes = paquetes.filter(fecha_registro__date=fecha)
    if estado:
        paquetes = paquetes.filter(estado=estado)

    entregas_totales = paquetes.filter(estado='entregado').count()
    entregas = paquetes.filter(
        estado='entregado',
        fecha_entrega__isnull=False,
        fecha_registro__isnull=False
    ).values_list('fecha_registro', 'fecha_entrega')
    diferencias = []
    for registro, entrega in entregas:
        #PARTE PARA CONVERTIR STRING A DATETIME(solo un if)
        if isinstance(registro, str):
            registro = datetime.strptime(registro, '%Y-%m-%d %H:%M:%S')
        if isinstance(entrega, str):
            entrega = datetime.strptime(entrega, '%Y-%m-%d %H:%M:%S')
        delta = entrega-registro
        diferencias.append(delta.total_seconds())

    #parte para calcular el promedio y convertirlo a horas
    if diferencias:
        segundos_promedio = sum(diferencias)/len(diferencias)
        min_promedios = round(segundos_promedio/60, 2)
    else:
        min_promedios = 0

    distancia_total = Ruta.objects.filter(conductorposeeruta__conductor=conductor).aggregate(total=Sum('distancia_km'))['total'] or 0
    dias_entregas = {}
    for paquete in paquetes.filter(estado='entregado'):
        fecha = paquete.fecha_entrega.date()
        dias_entregas[fecha] = dias_entregas.get(fecha, 0) + 1
    dia_mas_productivo = max(dias_entregas, key=lambda x: dias_entregas[x]) if dias_entregas else None
    clientes = Cliente.objects.select_related('usuario').all()

    return render(request, 'Conductor/rendimiento.html', {
        'clientes': clientes,
        'paquetes': paquetes.order_by('-id'),
        'entregas_totales': entregas_totales,
        'tiempo_promedio': min_promedios,
        'distancia_total': round(distancia_total, 2),
        'dia_mas_productivo': dia_mas_productivo,
    })

def cambiar_estado_paquete_conductor(request):
    if request.method == 'POST':
        paquete_id = request.POST.get('paquete_id')
        paquete = Paquete.objects.get(id=paquete_id)
        paquete.estado = request.POST.get('estado')
        paquete.save()
        notificar_cambio_estado_paquete(paquete)
    return redirect('conductor:paquetes')

def mapa(request):
    #conductor = Conductor.objects.get(usuario=request.user)             #DEPENDE DE ESTAR LOGEADO, ESTE DEBERÍA USARSE
    conductor = getattr(request.user, 'conductor', None)#DEPENDE DE ESTAR LOGEADO, SOLO PARA VER LA INTERFAZ
    paquetes = Paquete.objects.filter(conductor=conductor)

    id_paquete = request.GET.get('id')
    direccion_envio = request.GET.get('fecha')
    direccion_actual = request.GET.get('estado')
    
    return render(request, 'Conductor/mapa.html', {
        'paquetes_info': paquete_info,
    })