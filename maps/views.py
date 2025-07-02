from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utilities import obtener_coordenadas, calcular_ruta_entre_nodos, calcular_datos_ruta, decodificar_polyline
from geopy.exc import GeocoderTimedOut
import json

@login_required(login_url='/accounts/login/')
def map(request):
    inicio = request.GET.get('inicio', '')
    destino = request.GET.get('destino', '')

    if not inicio or not destino:
        messages.error(request, "Faltan parámetros en la solicitud.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        # Obtener coordenadas de inicio y destino
        inicio_coordenada = obtener_coordenadas(inicio)
        destino_coordenada = obtener_coordenadas(destino)

        if not inicio_coordenada or not destino_coordenada:
            messages.error(request, "No se pudo geolocalizar las direcciones.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        # Preparar nodos para la ruta de ida
        nodos_ida = [
            {'lat': inicio_coordenada[0], 'lon': inicio_coordenada[1]},
            {'lat': destino_coordenada[0], 'lon': destino_coordenada[1]}
        ]
        
        # Preparar nodos para la ruta de regreso
        nodos_regreso = [
            {'lat': destino_coordenada[0], 'lon': destino_coordenada[1]},
            {'lat': inicio_coordenada[0], 'lon': inicio_coordenada[1]}
        ]
        
        # Calcular ruta de ida y de regreso
        ruta_ida = calcular_ruta_entre_nodos(nodos_ida, roundtrip=False)
        ruta_regreso = calcular_ruta_entre_nodos(nodos_regreso, roundtrip=False)
        
        # Preparar datos para el template
        def procesar_ruta(ruta_detallada, nombre_ruta, color_ruta):
            """Función auxiliar para procesar una ruta y extraer sus coordenadas"""
            if not ruta_detallada:
                return None
                
            coordenadas_ruta = []
            
            # Si hay geometría completa, decodificarla
            if ruta_detallada.get('geometria_completa'):
                try:
                    # Decodificar la geometría polyline de OSRM usando la librería oficial
                    coordenadas_decodificadas = decodificar_polyline(ruta_detallada['geometria_completa'])
                    
                    print(f"Polyline {nombre_ruta} decodificado, primeras 3 coordenadas: {coordenadas_decodificadas[:3]}")
                    
                    # Convertir a formato [lat, lng] para Leaflet
                    coordenadas_ruta = [[lat, lng] for lat, lng in coordenadas_decodificadas]
                    
                    # Verificar si las coordenadas están en el rango correcto para Chile
                    if coordenadas_ruta and len(coordenadas_ruta) > 0:
                        primera_lat, primera_lng = coordenadas_ruta[0]
                        print(f"Primera coordenada {nombre_ruta}: [{primera_lat}, {primera_lng}]")
                        
                        # Verificar rango válido para Chile: Lat -56 a -17, Lng -109 a -66
                        if -56 <= primera_lat <= -17 and -109 <= primera_lng <= -66:
                            print(f"✅ Coordenadas {nombre_ruta} en rango válido para Chile")
                        else:
                            print(f"⚠️ Coordenadas {nombre_ruta} fuera del rango de Chile")
                            print(f"Lat: {primera_lat}, Lng: {primera_lng}")
                            print(f"Usando línea recta como fallback para {nombre_ruta}")
                            # En caso de coordenadas fuera de rango, usar línea recta
                            if "Ida" in nombre_ruta:
                                coordenadas_ruta = [[inicio_coordenada[0], inicio_coordenada[1]], 
                                                  [destino_coordenada[0], destino_coordenada[1]]]
                            else:  # regreso
                                coordenadas_ruta = [[destino_coordenada[0], destino_coordenada[1]], 
                                                  [inicio_coordenada[0], inicio_coordenada[1]]]
                    
                except Exception as e:
                    print(f"Error decodificando polyline {nombre_ruta}: {e}")
                    # En caso de error, usar coordenadas básicas
                    if "Ida" in nombre_ruta:
                        coordenadas_ruta = [[inicio_coordenada[0], inicio_coordenada[1]], 
                                          [destino_coordenada[0], destino_coordenada[1]]]
                    else:  # regreso
                        coordenadas_ruta = [[destino_coordenada[0], destino_coordenada[1]], 
                                          [inicio_coordenada[0], inicio_coordenada[1]]]
            else:
                # Si no hay geometría, usar coordenadas básicas
                if "Ida" in nombre_ruta:
                    coordenadas_ruta = [[inicio_coordenada[0], inicio_coordenada[1]], 
                                      [destino_coordenada[0], destino_coordenada[1]]]
                else:  # regreso
                    coordenadas_ruta = [[destino_coordenada[0], destino_coordenada[1]], 
                                      [inicio_coordenada[0], inicio_coordenada[1]]]
            
            # Procesar pasos para obtener coordenadas detalladas
            pasos_coordenadas = []
            for paso in ruta_detallada.get('pasos', []):
                paso_coords = []
                if paso.get('geometria'):
                    try:
                        # Decodificar geometría del paso individual usando la librería oficial
                        coords_paso = decodificar_polyline(paso['geometria'])
                        paso_coords = [[lat, lng] for lat, lng in coords_paso]
                        
                    except Exception as e:
                        print(f"Error decodificando polyline del paso {nombre_ruta}: {e}")
                        # Si falla, usar coordenadas básicas
                        if "Ida" in nombre_ruta:
                            paso_coords = [[inicio_coordenada[0], inicio_coordenada[1]], 
                                         [destino_coordenada[0], destino_coordenada[1]]]
                        else:  # regreso
                            paso_coords = [[destino_coordenada[0], destino_coordenada[1]], 
                                         [inicio_coordenada[0], inicio_coordenada[1]]]
                
                pasos_coordenadas.append({
                    'nombre': paso['nombre'],
                    'instruccion': paso.get('instruccion', ''),
                    'distancia': paso.get('distancia', 0),
                    'coordenadas': paso_coords
                })
            
            return {
                'coordenadas': coordenadas_ruta,
                'distancia_km': ruta_detallada.get('distancia_km', 0),
                'duracion_minutos': round(ruta_detallada.get('duracion_minutos', 0), 1),
                'color': color_ruta,
                'nombre': nombre_ruta,
                'pasos': pasos_coordenadas
            }
        
        # Procesar ruta de ida
        ruta_ida_procesada = procesar_ruta(ruta_ida, "Ruta de Ida", '#3388ff')
        # Procesar ruta de regreso
        ruta_regreso_procesada = procesar_ruta(ruta_regreso, "Ruta de Regreso", '#ff8833')
        
        # Preparar datos combinados para el template
        rutas_data = []
        distancia_total = 0
        duracion_total = 0
        
        if ruta_ida_procesada:
            rutas_data.append(ruta_ida_procesada)
            distancia_total += ruta_ida_procesada['distancia_km']
            duracion_total += ruta_ida_procesada['duracion_minutos']
            
        if ruta_regreso_procesada:
            rutas_data.append(ruta_regreso_procesada)
            distancia_total += ruta_regreso_procesada['distancia_km']
            duracion_total += ruta_regreso_procesada['duracion_minutos']
        
        # Si no hay rutas válidas, usar datos básicos
        if not rutas_data:
            datos_basicos = calcular_datos_ruta(inicio_coordenada, destino_coordenada)
            rutas_data = [{
                'coordenadas': [[inicio_coordenada[0], inicio_coordenada[1]], 
                              [destino_coordenada[0], destino_coordenada[1]]],
                'distancia_km': datos_basicos.get('distancia_km', 0),
                'duracion_minutos': datos_basicos.get('duracion_estimada_minutos', 0),
                'color': '#ff3388',
                'nombre': 'Ruta Básica',
                'pasos': []
            }]
            distancia_total = datos_basicos.get('distancia_km', 0)
            duracion_total = datos_basicos.get('duracion_estimada_minutos', 0)
        
        contexto = {
            'rutas_data': json.dumps(rutas_data),  # Lista de rutas (ida y regreso)
            'inicio_direccion': inicio,
            'destino_direccion': destino,
            'distancia_total': distancia_total,
            'duracion_total': duracion_total,
            'pagina_anterior': request.META.get('HTTP_REFERER', '/'),  # URL de la página anterior
        }
        
        return render(request, 'map.html', contexto)

    except GeocoderTimedOut:
        messages.error(request, "Tiempo de espera agotado al intentar geolocalizar la dirección.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    except Exception as e:
        messages.error(request, f"Error al calcular la ruta: {str(e)}")
        return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='/accounts/login/')
def map_paquete(request, paquete_id):
    """
    Vista para mostrar la ruta de un paquete específico desde la base de datos
    """
    try:
        from api.models import Paquete, Ruta
        
        # Obtener el paquete
        try:
            paquete = Paquete.objects.get(id=paquete_id)
        except Paquete.DoesNotExist:
            messages.error(request, f"Paquete con ID {paquete_id} no encontrado.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        # Verificar si existe una ruta calculada
        try:
            ruta = paquete.ruta
        except Ruta.DoesNotExist:
            messages.warning(request, "Ruta no calculada para este paquete. Calculando...")
            # Intentar calcular la ruta
            from .utilities import calcular_y_guardar_ruta_paquete
            ruta, error = calcular_y_guardar_ruta_paquete(paquete)
            
            if error:
                messages.error(request, f"No se pudo calcular la ruta: {error}")
                return redirect(request.META.get('HTTP_REFERER', '/'))
        
        # Preparar datos de rutas usando polylines si están disponibles
        from api.serializers import RutaSerializer
        serializer = RutaSerializer(ruta)
        
        if ruta.ruta_ida_polyline and ruta.ruta_regreso_polyline:
            rutas_data = serializer.get_rutas_data_polyline(ruta)
        else:
            rutas_data = serializer.get_rutas_data(ruta)
        
        contexto = {
            'rutas_data': json.dumps(rutas_data),
            'inicio_direccion': ruta.origen_direccion,
            'destino_direccion': ruta.destino_direccion,
            'distancia_total': ruta.distancia_total_km,
            'duracion_total': ruta.duracion_total_minutos,
            'paquete': paquete,
            'pagina_anterior': request.META.get('HTTP_REFERER', '/'),
        }
        
        return render(request, 'map.html', contexto)
        
    except Exception as e:
        messages.error(request, f"Error al cargar la ruta: {str(e)}")
        return redirect(request.META.get('HTTP_REFERER', '/'))
