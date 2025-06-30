from django.shortcuts import render
from api.models import Cliente, Paquete, Notificacion

# Create your views here.
def inicio(request):
    notificaciones = Notificacion.objects.all()
    paquetes = Paquete.objects.all()
    return render(request,'Cliente/inicio.html', context = {'notificaciones': notificaciones, 'paquetes':paquetes})

def mis_pedidos(request):
    paquetes = Paquete.objects.all()

    return render(request, 'Cliente/mis_pedidos.html', context = {'paquetes':paquetes})

def ayuda(request):

    return render(request,'Cliente/ayuda.html')