from django.http import HttpResponse
from django.template import Template, Context
from django.template import loader
from django.shortcuts import render, redirect
from api.models import Paquete, Cliente, Usuario, Despachador, Conductor
from django.contrib import messages
from django.views.decorators.http import require_POST
from accounts.views import notificar_cambio_estado_paquete

def inicio(request):
    from datetime import date
    from api.models import Paquete, Conductor
    
    # Obtener estadísticas
    paquetes_en_bodega = Paquete.objects.filter(estado='En_Bodega').count()
    paquetes_en_ruta = Paquete.objects.filter(estado='En_ruta').count()
    conductores_disponibles = Conductor.objects.filter(estado='disponible').count()
    
    # Paquetes entregados hoy
    paquetes_entregados_hoy = Paquete.objects.filter(
        estado='Entregado',
        fecha_entrega = date.today()
    ).count()
    
    context = {
        'paquetes_en_bodega': paquetes_en_bodega,
        'paquetes_en_ruta': paquetes_en_ruta,
        'conductores_disponibles': conductores_disponibles,
        'paquetes_entregados_hoy': paquetes_entregados_hoy,
    }
    
    return render(request, 'despachador/inicio.html', context)

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
    """
    Vista para registrar un nuevo paquete con confirmación de ubicación.
    
    Flujo:
    1. Usuario llena el formulario y envía
    2. Se guarda temporalmente en sesión
    3. Se redirige a confirmación de ubicación
    4. Usuario confirma/rechaza la ubicación
    5. Se guarda el paquete o se vuelve al formulario
    """
    from .forms import RegistroPaqueteForm
    
    # Verificar si se está regresando de la confirmación de ubicación
    ubicacion_confirmada = request.GET.get('ubicacion_confirmada')
    
    if ubicacion_confirmada is not None:
        # Se está regresando de la página de confirmación de ubicación
        return manejar_confirmacion_ubicacion(request, ubicacion_confirmada)
    
    if request.method == 'POST':
        
        # Procesamiento inicial del formulario
        form = RegistroPaqueteForm(request.POST)
        if form.is_valid():
            try:
                # Guardar los datos del formulario en la sesión para usar después
                request.session['paquete_form_data'] = request.POST.dict()
                
                # Obtener la dirección para confirmar
                direccion = form.cleaned_data['direccion_envio_texto']
                
                # Redirigir a la página de confirmación de ubicación
                from django.urls import reverse
                from urllib.parse import urlencode
                
                params = urlencode({'direccion': direccion})
                url = f"{reverse('maps:map_direccion')}?{params}"
                
                return redirect(url)
                
            except Exception as e:
                messages.error(request, f'Error al procesar el paquete: {str(e)}')
                return render(request, 'despachador/registrar_paquete.html', {'form': form})
        else:
            # Formulario no válido
            return render(request, 'despachador/registrar_paquete.html', {'form': form})
    else:
        # GET request - mostrar formulario vacío
        form = RegistroPaqueteForm()
        return render(request, 'despachador/registrar_paquete.html', {'form': form})

def manejar_confirmacion_ubicacion(request, ubicacion_confirmada):
    """
    Maneja la respuesta de la confirmación de ubicación.
    
    Args:
        request: HttpRequest object
        ubicacion_confirmada: 'true' si confirmó, 'false' si rechazó
    
    Returns:
        HttpResponse apropiado según la confirmación
    """
    from .forms import RegistroPaqueteForm
    
    # Recuperar los datos del formulario de la sesión
    form_data = request.session.get('paquete_form_data')
    if not form_data:
        messages.error(request, 'Se perdieron los datos del formulario. Por favor, inténtalo de nuevo.')
        return redirect('registrar_paquete')
    
    if ubicacion_confirmada == 'true':
        # Usuario confirmó la ubicación - guardar el paquete
        return procesar_ubicacion_confirmada(request, form_data)
    
    elif ubicacion_confirmada == 'false':
        # Usuario rechazó la ubicación - volver al formulario
        return procesar_ubicacion_rechazada(request, form_data)
    
    else:
        # Parámetro inválido
        messages.error(request, 'Parámetro de confirmación inválido.')
        form = RegistroPaqueteForm(form_data)
        return render(request, 'despachador/registrar_paquete.html', {'form': form})

def procesar_ubicacion_confirmada(request, form_data):
    """
    Procesa el caso cuando el usuario confirma la ubicación.
    """
    from .forms import RegistroPaqueteForm
    
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    
    if not lat or not lng:
        messages.error(request, 'No se recibieron las coordenadas confirmadas.')
        form = RegistroPaqueteForm(form_data)
        return render(request, 'despachador/registrar_paquete.html', {'form': form})
    
    try:
        # Crear el formulario con los datos guardados
        form = RegistroPaqueteForm(form_data)
        
        if form.is_valid():
            # Obtener el despachador
            despachador = Despachador.objects.get(usuario=request.user)
            
            # Guardar el paquete sin calcular coordenadas automáticamente
            paquete = form.save(commit=False, despachador=despachador, skip_coordinates=True)
            
            # Usar las coordenadas confirmadas por el usuario
            paquete.direccion_envio_lat = float(lat)
            paquete.direccion_envio_lng = float(lng)
            paquete.save()
            
            # Limpiar la sesión
            del request.session['paquete_form_data']
            
            messages.success(request, 'Paquete registrado exitosamente con ubicación confirmada.')
            return redirect('paquetes_despachador')
        else:
            messages.error(request, 'Error en los datos del formulario.')
            return render(request, 'despachador/registrar_paquete.html', {'form': form})
            
    except Despachador.DoesNotExist:
        messages.error(request, 'No se encontró el despachador asociado a tu usuario.')
        form = RegistroPaqueteForm(form_data)
        return render(request, 'despachador/registrar_paquete.html', {'form': form})
        
    except ValueError as e:
        messages.error(request, 'Las coordenadas recibidas no son válidas.')
        form = RegistroPaqueteForm(form_data)
        return render(request, 'despachador/registrar_paquete.html', {'form': form})
        
    except Exception as e:
        messages.error(request, f'Error al registrar el paquete: {str(e)}')
        form = RegistroPaqueteForm(form_data)
        return render(request, 'despachador/registrar_paquete.html', {'form': form})

def procesar_ubicacion_rechazada(request, form_data):
    """
    Procesa el caso cuando el usuario rechaza la ubicación.
    """
    from .forms import RegistroPaqueteForm
    
    # Volver al formulario con los datos originales
    form = RegistroPaqueteForm(form_data)
    messages.warning(request, 
        'Ubicación no confirmada. Por favor, ingresa una dirección más específica y detallada.')
    
    # No limpiar la sesión para que el usuario pueda volver a intentar
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
        nuevo_estado = request.POST.get('estado')
        estado_antiguo = paquete.estado
        print(f"estado_antiguo = {estado_antiguo}")
        paquete.estado = nuevo_estado
        print(f"estado_nuevo = {nuevo_estado}")
        
        # Si el estado cambia a "Entregado", establecer la fecha de entrega
        if nuevo_estado == 'Entregado':
            from datetime import date
            paquete.fecha_entrega = date.today()
        
        paquete.save()
        notificar_cambio_estado_paquete(paquete, estado_antiguo)
    return redirect('paquetes_despachador')