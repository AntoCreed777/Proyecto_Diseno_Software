from django.shortcuts import render
import json
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required(login_url='/accounts/login/')
def map(request):

    # La direccion que esta en el contexto se debe de recibir usando ''request.POST.get('direccion')''
    # Cambiar cuando se haya implementado el formulario
    # En este caso se esta usando una direccion de ejemplo
    
    contexto = {
        'direccion_lenguaje_natural': "Edmundo Larenas, Concepcion, Chile",
        'nodos': json.dumps([
            {'lat': -36.826, 'lon': -73.049},
            {'lat': -36.827, 'lon': -73.048},
            {'lat': -36.828, 'lon': -73.047},
            {'lat': -36.829, 'lon': -73.046},
        ]),
    }
    return render(request, 'map.html', contexto)