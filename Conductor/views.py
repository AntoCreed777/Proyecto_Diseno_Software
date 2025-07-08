from django.shortcuts import render, redirect
from api.models import Paquete, Ruta, TiposRoles
from datetime import datetime,date 
from accounts.views import notificar_cambio_estado_paquete
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Sum
from django.shortcuts import redirect
from django.contrib import messages
from api.groups_decorator import group_required

@group_required(TiposRoles.CONDUCTOR)
def inicio(request):
    conductor = request.user.conductor 
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

    paquetes_totales = Paquete.objects.filter(conductor=conductor)
    rutas_asignadas = Ruta.objects.filter(paquete__conductor=conductor).distinct().count()
    paquetes_pendientes = paquetes_totales.filter(estado='En_Bodega').count()
    paquetes_en_curso = paquetes_totales.filter(estado='En_ruta').count()
    paquetes_entregados = paquetes_totales.filter(estado='Entregado').count()

    total_paquetes_asignados = paquetes_totales.count()
    rendimiento = (paquetes_entregados/total_paquetes_asignados * 100) if total_paquetes_asignados > 0 else 0
    
    return render(request, 'Conductor/inicio.html', {
        'paquetes': paquetes.order_by('-id'),
        'rutas_asignadas': rutas_asignadas,
        'paquetes_pendientes': paquetes_pendientes,
        'paquetes_en_curso': paquetes_en_curso,
        'paquetes_entregados': paquetes_entregados,
        'rendimiento': round(rendimiento, 2)
    })

@group_required(TiposRoles.CONDUCTOR)
def paquetes(request):
    conductor = request.user.conductor
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

    return render(request, 'Conductor/paquetes.html', {
        'paquetes': paquetes.order_by('-id'),
    })

@group_required(TiposRoles.CONDUCTOR)
def actualizar_ruta(request):
    if request.method == 'POST':
        paquete_id = request.POST.get('paquete_id')
        accion = request.POST.get('accion')
        
        try:
            paquete = Paquete.objects.get(id=paquete_id, conductor=request.user.conductor)
            ruta, created = Ruta.objects.get_or_create(paquete=paquete)
            
            if accion == 'iniciar':
                ruta.fecha_inicio_ruta = datetime.now()
                paquete.estado = 'En_ruta'
                messages.success(request, f'Ruta para el paquete #{paquete_id} iniciada correctamente')
            elif accion == 'finalizar':
                ruta.fecha_fin_ruta = datetime.now()
                paquete.estado = 'Entregado'
                paquete.fecha_entrega = datetime.now()
                messages.success(request, f'Ruta para el paquete #{paquete_id} finalizada correctamente')
            
            ruta.save()
            paquete.save()
            
        except Paquete.DoesNotExist:
            messages.error(request, 'Paquete no encontrado')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return redirect('conductor:paquetes')

@group_required(TiposRoles.CONDUCTOR)
def rendimiento(request):
    conductor = request.user.conductor

    id_paquete = request.GET.get('id')
    fecha = request.GET.get('fecha')
    estado = request.GET.get('estado')
    hoy = date.today()

    paquetes = Paquete.objects.filter(conductor=conductor)
    if id_paquete:
        paquetes = paquetes.filter(id=id_paquete)
    if fecha:
        paquetes = paquetes.filter(fecha_registro__date=fecha)
    if estado:
        paquetes = paquetes.filter(estado=estado)


    entregas_totales = paquetes.filter(estado='Entregado').count()

    distancia_total = Ruta.objects.filter(paquete__conductor=conductor).aggregate(
        total=Sum('distancia_total_km')
    )['total'] or 0


    entregas_hoy = paquetes.filter(estado='Entregado', fecha_entrega__date=hoy)
    for paquete in entregas_hoy:
        if paquete.fecha_registro and paquete.fecha_entrega:
            delta = paquete.fecha_entrega-paquete.fecha_registro
            paquete.tiempo_entrega_min = round(delta.total_seconds() / 3600, 2)
        else:
            paquete.tiempo_entrega_min = 0
        
        try:
            ruta = Ruta.objects.get(paquete=paquete)
            paquete.distancia_km = round(ruta.distancia_total_km,2)
        except Ruta.DoesNotExist:
            paquete.distancia_km = 0

    number=0
    h_total=0
    for paquete in entregas_hoy:
        if paquete.tiempo_entrega_min:
            h_total+=paquete.tiempo_entrega_min
            number+=1
        else:
            None
    
    if number>0:
        h_promedios = round(h_total / number, 2)
    else:
        h_promedios=0
    

    return render(request, 'Conductor/rendimiento.html', {
        'paquetes': paquetes.order_by('-id'),
        'entregas_totales': entregas_totales,
        'entregas_hoy': entregas_hoy,
        'tiempo_promedio': h_promedios,
        'distancia_total': round(distancia_total, 2),
    })

def cambiar_estado_paquete_conductor(request):
    if request.method == 'POST':
        paquete_id = request.POST.get('paquete_id')
        nuevo_estado = request.POST.get('estado')
        
        if not paquete_id or not nuevo_estado:
            return redirect('conductor:paquetes')
        
        paquete = get_object_or_404(Paquete, id=paquete_id)
        
        if not request.user.is_authenticated or not hasattr(request.user, 'conductor'):
            return redirect('conductor:paquetes')
        
        if paquete.conductor != request.user.conductor:
            return redirect('conductor:paquetes')
        
        paquete.estado = nuevo_estado
        
        if nuevo_estado == 'Entregado':
            paquete.fecha_entrega = datetime.now()
        
        paquete.save()
        notificar_cambio_estado_paquete(paquete, nuevo_estado)
    
    return redirect('conductor:paquetes')

def mapa(request):
    id_paquete = request.GET.get('id')

    if not id_paquete:
        return redirect('conductor:paquetes')

    paquete = get_object_or_404(Paquete, id=id_paquete)
    
    if not request.user.is_authenticated or not hasattr(request.user, 'conductor'):
        return redirect('conductor:paquetes')
    
    if paquete.conductor != request.user.conductor:
        return redirect('conductor:paquetes')

    url = reverse('maps:map_paquete', kwargs={'paquete_id': id_paquete})
    return redirect(url)
