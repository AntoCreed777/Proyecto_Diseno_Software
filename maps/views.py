from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required(login_url='/accounts/login/')
def map(request):
    inicio = request.GET.get('inicio', '')
    destino = request.GET.get('destino', '')

    if not inicio or not destino:
        return HttpResponse("Faltan parámetros en la solicitud", status=400)

    print(inicio)
    print(destino)

    contexto = {
        'inicio': inicio,
        'destino': destino
    }
    
    return render(request, 'map.html', contexto)
