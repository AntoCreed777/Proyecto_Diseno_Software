from django.shortcuts import render
from api.models import Cliente, Paquete

# Create your views here.
def inicio(request):

    return render(request,'Cliente/inicio.html')

def mis_pedidos(request):

    clientes = Cliente.objects.all()
    paquetes = Paquete.objects.all()

    print(clientes)
    return render(request, 'Cliente/mis_pedidos.html', context = {'paquetes':paquetes})

def ayuda(request):

    return render(request,'Cliente/ayuda.html')