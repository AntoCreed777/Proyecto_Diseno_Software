from django.http import HttpResponse
from django.template import Template, Context
from django.template import loader
from django.shortcuts import render

# Create your views here.

def inicio(request):

    return render(request,'Conductor/inicio.html')

def paquetes(request):

    return render(request,'Conductor/paquetes.html')

def rendimiento(request):

    return render(request,'Conductor/conductores.html')