"""
Constantes para el módulo de mapas y rutas.

Este archivo contiene las constantes utilizadas en todo el sistema para la gestión de rutas,
especialmente la información de la Universidad de Concepción como punto de origen fijo.
"""

# Información de la Universidad de Concepción
UNIVERSIDAD_CONCEPCION = {
    "direccion": "Universidad de Concepcion, Concepcion, Bio Bio, Chile",
    "coordenadas": {
        "latitud": -36.8302049,
        "longitud": -73.0372293
    },
    "nombre": "Universidad de Concepción"
}

# Coordenadas como tupla para compatibilidad con funciones existentes
UNIVERSIDAD_CONCEPCION_COORDS_TUPLE = (
    UNIVERSIDAD_CONCEPCION["coordenadas"]["latitud"],
    UNIVERSIDAD_CONCEPCION["coordenadas"]["longitud"]
)

# Configuración para APIs de mapas
MAPA_CONFIG = {
    "radio_busqueda_nodos": 50,  # metros
    "timeout_requests": 30,      # segundos
    "precision_distancia": 2,    # decimales para distancias en km
    "precision_duracion": 1      # decimales para duración en minutos
}

# URLs de servicios externos
API_URLS = {
    "overpass": "https://overpass-api.de/api/interpreter",
    "osrm_route": "https://router.project-osrm.org/route/v1/driving"
}
