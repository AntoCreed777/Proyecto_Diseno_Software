from django.shortcuts import render, redirect
from api.models import Paquete, Cliente, Despachador, Conductor, Ruta, TiposRoles
from api.serializers import PaqueteSerializer
from django.contrib import messages
from accounts.views import notificar_cambio_estado_paquete
from maps.utilities import obtener_coordenadas
from api.groups_decorator import group_required

@group_required(TiposRoles.ADMIN)
def inicio(request):
    
    # Obtener estadísticas
    paquetes_en_bodega = Paquete.objects.filter(estado='En_Bodega').count()
    paquetes_en_ruta = Paquete.objects.filter(estado='En_ruta').count()
    conductores_disponibles = Conductor.objects.filter(estado='disponible').count()
    
    # Paquetes entregados hoy
    paquetes_entregados = Paquete.objects.filter(estado='Entregado').count()
    
    context = {
        'paquetes_en_bodega': paquetes_en_bodega,
        'paquetes_en_ruta': paquetes_en_ruta,
        'conductores_disponibles': conductores_disponibles,
        'paquetes_entregados': paquetes_entregados,
    }
    return render(request,'administrador/inicio.html',context)

@group_required(TiposRoles.ADMIN)
def graficas(request):
   
    rutas = Ruta.objects.all()
    rutas_json = list(rutas.values('distancia_ida_km','distancia_regreso_km','distancia_total_km'))
    return render(request, 'administrador/graficas.html', {
        'rutas': rutas,
        'rutas_json': rutas_json
    })

@group_required(TiposRoles.ADMIN)
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
    return render(request, 'administrador/paquetes.html', {
        'clientes': clientes,
        'paquetes': paquetes.order_by('-id'),
        'conductores': conductores,
    })

@group_required(TiposRoles.ADMIN)
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

    return render(request, 'administrador/conductores.html', {'conductores': conductores})

def registrar_paquete(request):
    if request.method == 'POST':
        dimensiones = request.POST.get('dimensiones', '')
        try:
            largo, ancho, alto = [float(x.strip()) for x in dimensiones.lower().replace(' ', '').split('x')]
        except Exception:
            messages.error(request, "Formato de dimensiones inválido. Use 'largo x ancho x alto'.")
            clientes = Cliente.objects.select_related('usuario').all()
            return render(request, 'administrador/registrar_paquete.html', {
                'clientes': clientes,
                'errors_paquete': {'dimensiones': ['Formato inválido. Use "largo x ancho x alto".']},
            })
        
        direccion_envio_texto = request.POST.get('direccion_envio_texto')
        direccion_envio_lat = 0.0
        direccion_envio_lng = 0.0
        
        try:
            coordenadas_envio = obtener_coordenadas(direccion_envio_texto)
            if coordenadas_envio:
                direccion_envio_lat = coordenadas_envio[0]
                direccion_envio_lng = coordenadas_envio[1]
            else:
                messages.warning(request, "No se pudieron obtener las coordenadas de la dirección de envío. Se usarán coordenadas por defecto.")
        except:
            messages.warning(request, "Error al obtener coordenadas de la dirección. Se usarán coordenadas por defecto.")
        
        data = {
            'largo': largo,
            'ancho': ancho,
            'alto': alto,
            'peso': request.POST.get('peso'),
            'direccion_envio_lat': direccion_envio_lat,
            'direccion_envio_lng': direccion_envio_lng,
            'direccion_envio_texto': direccion_envio_texto,
            'nombre_destinatario': request.POST.get('nombre_destinatario'),
            'rut_destinatario': request.POST.get('rut_destinatario'),
            'telefono_destinatario': request.POST.get('telefono_destinatario'),
            'cliente': request.POST.get('cliente_id'),
            'despachador': Despachador.objects.first().pk,
        }
        
        serializer = PaqueteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Paquete registrado exitosamente.')
            return redirect('paquetes_administrador')
        else:
            clientes = Cliente.objects.select_related('usuario').all()
            return render(request, 'administrador/registrar_paquete.html', {
                'clientes': clientes,
                'errors_paquete': serializer.errors,
            })
    else:
        clientes = Cliente.objects.select_related('usuario').all()
        return render(request, 'administrador/registrar_paquete.html', {
            'clientes': clientes,
        })

def registrar_cliente(request):
    from accounts.forms import RegistroClienteForm
    from accounts.views import activarEmail

    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=True)
            activarEmail(request, usuario)
            messages.success(request, 'Cliente registrado exitosamente. Se ha enviado un correo de verificación.')
            return redirect('paquetes_administrador')
        else:
            return render(request, 'administrador/registrar_cliente.html', {'form': form})
    else:
        form = RegistroClienteForm()
        return render(request, 'administrador/registrar_cliente.html', {'form': form})

def asignar_conductor(request):
    if request.method == 'POST':
        paquete_id = request.POST.get('paquete_id')
        conductor_id = request.POST.get('conductor_id')
        paquete = Paquete.objects.get(id=paquete_id)
        conductor = Conductor.objects.get(id=conductor_id)
        paquete.conductor = conductor
        paquete.save()
    return redirect('paquetes_administrador')

def cambiar_estado_paquete(request):
    if request.method == 'POST':
        paquete_id = request.POST.get('paquete_id')
        paquete = Paquete.objects.get(id=paquete_id)
        
        if paquete.estado == request.POST.get('paquete_id'):
            return redirect('paquetes_administrador')
        
        estado_antiguo = paquete.estado
        paquete.estado = request.POST.get('estado')
        
        # Si el estado cambia a "Entregado", establecer la fecha de entrega
        if paquete.estado == 'Entregado':
            from datetime import date
            paquete.fecha_entrega = date.today()
        
        paquete.save()
        notificar_cambio_estado_paquete(paquete, estado_antiguo)
    return redirect('paquetes_administrador')

def cambiar_direccion(request):
    if request.method == 'POST':
        paquete_id = request.POST.get('paquete_id')
        paquete = Paquete.objects.get(id=paquete_id)
        nueva_direccion = request.POST.get('cambiar_direccion')
        paquete.save()
        serializer = PaqueteSerializer()
        try:
            paquete_actualizado = serializer.update(paquete, {'direccion_envio_texto': nueva_direccion})
        except Exception as e:
            print(f"Error al actualizar el paquete {paquete.id}: {e}")
    return redirect('paquetes_administrador')