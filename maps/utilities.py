from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from typing import Dict, Tuple, List, Optional
import requests
import math
import polyline

def obtener_coordenadas(direccion):
    """
    Obtiene las coordenadas geográficas (latitud, longitud) a partir de una dirección textual.

    Parámetros:
        direccion (str): Dirección en formato "Calle y número, Ciudad, Región/Estado, País".
            Ejemplo: "Pasaje 1 #2693, Concepcion, Bio Bio, Chile"

    Retorna:
        tuple: (latitud, longitud) si la dirección es válida.
        None: Si la dirección no se encuentra o ocurre un error.
    """
    geolocator = Nominatim(user_agent="maps")
    try:
        location = geolocator.geocode(direccion)
        if location:
            return (location.latitude, location.longitude)
        else:
            return None  # Dirección no encontrada o mal escrita
    except GeocoderTimedOut as e:
        raise e

def calcular_datos_ruta(origen: Tuple[float, float], destino: Tuple[float, float]) -> Dict[str, float]:
    """
    Calcula datos de ruta entre origen y destino.
    
    Args:
        origen: Tupla (latitud, longitud) del punto de origen
        destino: Tupla (latitud, longitud) del punto de destino
    
    Returns:
        Dict con duracion_estimada_minutos y distancia_km
    """
    # Convertir tuplas a formato de nodos
    nodos = [
        {'lat': origen[0], 'lon': origen[1]},
        {'lat': destino[0], 'lon': destino[1]}
    ]
    
    # Calcular ruta sin roundtrip (solo ida)
    resultado_ruta = calcular_ruta_entre_nodos(nodos, roundtrip=False)
    
    if resultado_ruta:
        return {
            "duracion_estimada_minutos": round(resultado_ruta['duracion_minutos']),
            "distancia_km": round(resultado_ruta['distancia_km'], 2)
        }
    else:
        # Valores por defecto si no se puede calcular la ruta
        return {
            "duracion_estimada_minutos": 0,
            "distancia_km": 0
        }

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula la distancia entre dos puntos usando la fórmula de Haversine.
    
    Args:
        lat1, lon1: Latitud y longitud del primer punto
        lat2, lon2: Latitud y longitud del segundo punto
    
    Returns:
        float: Distancia en metros
    """
    R = 6371000  # Radio de la Tierra en metros
    
    # Convertir grados a radianes
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Diferencias
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Fórmula de Haversine
    a = (math.sin(dlat/2)**2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def encontrar_nodo_mas_cercano(lat: float, lon: float, nodos: List[Dict]) -> Optional[Dict]:
    """
    Encuentra el nodo más cercano a un punto dado.
    
    Args:
        lat, lon: Coordenadas del punto de referencia
        nodos: Lista de nodos con keys 'lat' y 'lon'
    
    Returns:
        Dict: Nodo más cercano o None si no hay nodos
    """
    if not nodos:
        return None
    
    nodo_cercano = None
    min_dist = float('inf')
    
    for nodo in nodos:
        dist = haversine_distance(lat, lon, nodo['lat'], nodo['lon'])
        if dist < min_dist:
            min_dist = dist
            nodo_cercano = nodo
    
    return nodo_cercano

def obtener_nodos_cercanos(lat: float, lon: float, radius: int = 50) -> List[Dict]:
    """
    Obtiene nodos de calles cercanos a una ubicación usando Overpass API.
    
    Args:
        lat, lon: Coordenadas del punto
        radius: Radio de búsqueda en metros
    
    Returns:
        List[Dict]: Lista de nodos cercanos
    """
    try:
        # Consulta para obtener ways cercanos
        query = f"""
        [out:json];
        way(around:{radius},{lat},{lon})["highway"];
        out body;
        """
        
        url = "https://overpass-api.de/api/interpreter"
        response = requests.post(url, data={'data': query}, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('elements'):
            return []
        
        # Extraer IDs de nodos de los ways
        node_ids = []
        for way in data['elements']:
            if 'nodes' in way:
                node_ids.extend(way['nodes'])
        
        if not node_ids:
            return []
        
        # Consulta para obtener las coordenadas de los nodos
        nodes_query = f"""
        [out:json];
        node(id:{','.join(map(str, node_ids))});
        out body;
        """
        
        nodes_response = requests.post(url, data={'data': nodes_query}, timeout=30)
        nodes_response.raise_for_status()
        
        nodes_data = nodes_response.json()
        
        return nodes_data.get('elements', [])
        
    except requests.RequestException as e:
        print(f"Error al obtener nodos cercanos: {e}")
        return []

def calcular_ruta_entre_nodos(nodos: List[Dict], roundtrip: bool = True) -> Optional[Dict]:
    """
    Calcula la ruta entre nodos usando OSRM y obtiene información detallada.
    Adaptación de la función JavaScript calcularRutaEntreNodos.
    
    Args:
        nodos: Lista de nodos con keys 'lat' y 'lon'
        roundtrip: Si debe regresar al punto inicial
    
    Returns:
        Dict: Información de la ruta con distancia, duración y pasos, o None si hay error
    """
    try:
        if len(nodos) < 2:
            print("Se necesitan al menos 2 nodos para calcular una ruta.")
            return None
        
        nodos_ruta = nodos.copy()
        
        if roundtrip:
            nodos_ruta.append(nodos[0])
        
        # Encontrar nodos más cercanos a las calles para cada punto
        nodos_optimizados = []
        for nodo in nodos_ruta:
            nodos_cercanos = obtener_nodos_cercanos(nodo['lat'], nodo['lon'], 50)
            if nodos_cercanos:
                nodo_cercano = encontrar_nodo_mas_cercano(nodo['lat'], nodo['lon'], nodos_cercanos)
                if nodo_cercano:
                    nodos_optimizados.append(nodo_cercano)
                else:
                    nodos_optimizados.append(nodo)
            else:
                nodos_optimizados.append(nodo)
        
        # Crear string de coordenadas para OSRM (lon,lat)
        coordenadas = ";".join([f"{nodo['lon']},{nodo['lat']}" for nodo in nodos_optimizados])
        
        # URL para OSRM Route API
        route_url = f"https://router.project-osrm.org/route/v1/driving/{coordenadas}?overview=full&steps=true"
        
        response = requests.get(route_url, timeout=30)
        response.raise_for_status()
        
        route_data = response.json()
        
        if not route_data.get('routes') or len(route_data['routes']) == 0:
            print("No se encontró una ruta con detalles.")
            return None
        
        # Obtener la primera ruta
        route = route_data['routes'][0]
        
        # Extraer información básica
        distancia_metros = route['distance']
        duracion_segundos = route['duration']
        
        # Extraer pasos detallados
        pasos = []
        for leg in route['legs']:
            for step in leg['steps']:
                paso = {
                    'nombre': step.get('name', 'Sin nombre'),
                    'distancia': step.get('distance', 0),
                    'duracion': step.get('duration', 0),
                    'geometria': step.get('geometry', ''),
                    'instruccion': step.get('maneuver', {}).get('instruction', '')
                }
                pasos.append(paso)
        
        resultado = {
            'distancia_km': distancia_metros / 1000,
            'duracion_minutos': duracion_segundos / 60,
            'distancia_metros': distancia_metros,
            'duracion_segundos': duracion_segundos,
            'pasos': pasos,
            'geometria_completa': route.get('geometry', ''),
            'nodos_optimizados': nodos_optimizados
        }
        
        print(f"Ruta calculada: {resultado['distancia_km']:.2f} km en {resultado['duracion_minutos']:.1f} minutos.")
        
        return resultado
        
    except requests.RequestException as e:
        print(f"Error al calcular la ruta: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al calcular la ruta: {e}")
        return None

def decodificar_polyline(encoded):
    """
    Decodifica una cadena de polyline codificada de Google/OSRM a una lista de coordenadas.
    Usa la librería polyline oficial para garantizar decodificación correcta.
    
    Args:
        encoded (str): Cadena polyline codificada
    
    Returns:
        List[Tuple[float, float]]: Lista de tuplas (latitud, longitud)
    """
    if not encoded:
        return []
    
    try:
        # Usar la librería polyline oficial para decodificar
        coordinates = polyline.decode(encoded)
        
        # Debug: mostrar las primeras coordenadas decodificadas
        if coordinates and len(coordinates) > 0:
            print(f"Debug decodificar_polyline: Primera coordenada (lat, lng): {coordinates[0]}")
            print(f"Debug decodificar_polyline: Total de coordenadas: {len(coordinates)}")
            
            # Verificar si las coordenadas están en rango correcto para Chile
            lat_test, lng_test = coordinates[0]
            if -56 <= lat_test <= -17 and -109 <= lng_test <= -66:
                print(f"✅ Coordenadas decodificadas correctamente en rango de Chile")
            else:
                print(f"⚠️ Advertencia: Coordenadas decodificadas fuera del rango de Chile")
                print(f"Coordenada: Lat {lat_test}, Lng {lng_test}")
        
        return coordinates
        
    except Exception as e:
        print(f"Error decodificando polyline con librería oficial: {e}")
        print(f"Intentando decodificación manual...")
        
        # Fallback a decodificación manual
        return decodificar_polyline_manual(encoded)

def decodificar_polyline_manual(encoded):
    """
    Implementación manual de decodificación de polyline como fallback.
    """
    if not encoded:
        return []
    
    index = 0
    lat = 0
    lng = 0
    coordinates = []
    
    while index < len(encoded):
        # Decodificar latitud
        result = 1
        shift = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result += (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        
        # Aplicar correctamente el signo para latitud
        delta_lat = ~(result >> 1) if result & 1 else result >> 1
        lat += delta_lat
        
        # Decodificar longitud
        result = 1
        shift = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result += (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        
        # Aplicar correctamente el signo para longitud
        delta_lng = ~(result >> 1) if result & 1 else result >> 1
        lng += delta_lng
        
        # Convertir a coordenadas decimales
        final_lat = lat / 1e5
        final_lng = lng / 1e5
        
        coordinates.append((final_lat, final_lng))
    
    print(f"Debug decodificar_polyline_manual: {len(coordinates)} coordenadas decodificadas")
    if coordinates:
        print(f"Primera coordenada manual: {coordinates[0]}")
    
    return coordinates

# Ejemplo de uso
if __name__ == '__main__':
    # Ejemplo 1: Obtener coordenadas de una dirección
    direccion = "Universidad de Concepcion, Concepcion, Bio Bio, Chile"
    
    try:
        coordenadas = obtener_coordenadas(direccion=direccion)
        if not coordenadas:
            print("Dirección no encontrada")
        else:
            latitud, longitud = coordenadas
            print(f"Latitud: {latitud}, Longitud: {longitud}")
            
            # Ejemplo 2: Calcular ruta entre dos puntos
            origen = (latitud, longitud)
            destino = (-36.8400, -73.0500)  # Otro punto en Concepción
            
            datos_ruta = calcular_datos_ruta(origen, destino)
            print(f"Datos de ruta: {datos_ruta}")
            
            # Ejemplo 3: Calcular ruta detallada entre múltiples nodos
            nodos = [
                {'lat': latitud, 'lon': longitud},
                {'lat': -36.8400, 'lon': -73.0500},
                {'lat': -36.8200, 'lon': -73.0400}
            ]
            
            ruta_detallada = calcular_ruta_entre_nodos(nodos, roundtrip=True)
            if ruta_detallada:
                print(f"Ruta detallada:")
                print(f"  - Distancia: {ruta_detallada['distancia_km']:.2f} km")
                print(f"  - Duración: {ruta_detallada['duracion_minutos']:.1f} minutos")
                print(f"  - Número de pasos: {len(ruta_detallada['pasos'])}")

    except GeocoderTimedOut:
        print("Tiempo de espera agotado al intentar geolocalizar la dirección")
