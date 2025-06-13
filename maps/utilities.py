from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

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

# Ejemplo de uso
if __name__ == '__main__':
    direccion = "Universidad de Concepcion, Concepcion, Bio Bio, Chile"

    try:
        coordenadas = obtener_coordenadas(direccion=direccion)
        if not coordenadas:
            print("Dirección no encontrada")
        else:
            latitud, longitud = coordenadas
            print(f"Latitud: {latitud}, Longitud: {longitud}")
    except GeocoderTimedOut:
        print("Tiempo de espera agotado al intentar geolocalizar la dirección")
