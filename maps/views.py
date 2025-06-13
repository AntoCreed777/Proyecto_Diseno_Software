from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utilities import obtener_coordenadas
from geopy.exc import GeocoderTimedOut
import json

@login_required(login_url='/accounts/login/')
def map(request):
    inicio = request.GET.get('inicio', '')
    destino = request.GET.get('destino', '')

    if not inicio or not destino:
        messages.error(request, "Faltan parámetros en la solicitud.")
        return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirige a la pagina de origen

    try:
        inicio_coordenada = obtener_coordenadas(inicio)
        destino_coordenada = obtener_coordenadas(destino)

        if not inicio_coordenada or not destino_coordenada:
            messages.error(request, "No se pudo geolocalizar las direcciones.")
            return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirige a la pagina de origen
        
        contexto = {
            'nodos': json.dumps([
                    {'lat': inicio_coordenada[0], 'lon': inicio_coordenada[1]},
                    {'lat': destino_coordenada[0], 'lon': destino_coordenada[1]},
            ])
        }
        return render(request, 'map.html', contexto)

    except GeocoderTimedOut:
        messages.error(request, "Tiempo de espera agotado al intentar geolocalizar la dirección.")
        return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirige a la pagina de origen
