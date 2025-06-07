from django.shortcuts import render
from api.models import Cliente

# Create your views here.
def inicio(request):

    return render(request,'Cliente/inicio.html')

def mis_pedidos(request):
    if hasattr(request.user, 'cliente'):
        clientes = Cliente.objects.all()
    else:
        clientes = "No hay clientes"

    print(clientes)
    return render(request, 'Cliente/mis_pedidos.html')

def ayuda(request):

    return render(request,'Cliente/ayuda.html')