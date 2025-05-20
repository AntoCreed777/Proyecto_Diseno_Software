from django.shortcuts import render

# Create your views here.
def map(request):

    # La direccion que esta en el contexto se debe de recibir usando ''request.POST.get('direccion')''
    # Cambiar cuando se haya implementado el formulario
    # En este caso se esta usando una direccion de ejemplo
    
    contexto = {
        'direccion_lenguaje_natural': "Edmundo Larenas, Concepcion, Chile",
        # 'direccion_lenguaje_natural': request.POST.get('direccion'),
    }
    return render(request, 'map.html', contexto)
