from django.http import HttpResponse
from django.template import Template, Context
from django.template import loader
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from api.models import ConductorPoseeRuta, Paquete, Notificacion, Conductor
from api.serializers import NotificacionSerializer
from datetime import datetime, timedelta 
from django.db.models import Q
# Create your views here.

@login_required
def inicio_conductor(request):
    # Obtener el conductor actual
    conductor = request.user.conductor
    
    # 1. Rutas asignadas
    rutas_asignadas = ConductorPoseeRuta.objects.filter(conductor=conductor).count()
    
    # 2. Paquetes por entregar
    paquetes_pendientes = Paquete.objects.filter(
        conductor_asignado=conductor,
        estado='en_camino'
    ).count()
    
    # 3. Paquetes entregados hoy
    hoy = datetime.now().date()
    paquetes_entregados = Paquete.objects.filter(
        conductor_asignado=conductor,
        estado='entregado',
        fecha_entrega__date=hoy
    ).count()
    
    # 4. Rendimiento (porcentaje de paquetes entregados hoy vs asignados)
    total_asignados_hoy = Paquete.objects.filter(
        conductor_asignado=conductor,
        fecha_asignacion__date=hoy
    ).count()
    
    rendimiento = 0
    if total_asignados_hoy > 0:
        rendimiento = round((paquetes_entregados / total_asignados_hoy) * 100)
    
    # Notificaciones recientes (últimas 5)
    notificaciones = Notificacion.objects.filter(
        usuario=request.user
    ).order_by('-fecha_hora')[:5]
    
    # Serializar notificaciones
    notificaciones_serializadas = NotificacionSerializer(notificaciones, many=True).data
    
    context = {
        'rutas_asignadas': rutas_asignadas,
        'paquetes_pendientes': paquetes_pendientes,
        'paquetes_entregados': paquetes_entregados,
        'rendimiento': f"{rendimiento}%",
        'notificaciones': notificaciones_serializadas,
    }
    
    return render(request, 'Conductor/inicio.html', context)

def inicio(request):

    return render(request,'Conductor/inicio.html')

def paquetes(request):

    return render(request,'Conductor/paquetes.html')

def rendimiento(request):

    return render(request,'Conductor/rendimiento.html')