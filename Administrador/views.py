from django.shortcuts import render

# Create your views here.

def inicio(request):

    return render(request,'Administrador/inicio.html')

def paquetes(request):

    return render(request,'Administrador/paquetes.html')

def conductores(request):

    return render(request,'Administrador/conductores.html')