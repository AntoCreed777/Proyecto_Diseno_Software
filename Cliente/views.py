from django.shortcuts import render
from api.models import Paquete, Notificacion, TiposRoles
from api.groups_decorator import group_required

@group_required(TiposRoles.CLIENTE)
def inicio(request):
    notificaciones = Notificacion.objects.all()
    paquetes = Paquete.objects.all()
    return render(request,'Cliente/inicio.html', context = {'notificaciones': notificaciones, 'paquetes':paquetes})

@group_required(TiposRoles.CLIENTE)
def mis_paquetes(request):
    paquetes = Paquete.objects.all()

    return render(request, 'Cliente/mis_paquetes.html', context = {'paquetes':paquetes})

@group_required(TiposRoles.CLIENTE)
def ayuda(request):
    return render(request,'Cliente/ayuda.html')