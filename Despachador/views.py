from django.http import HttpResponse
from django.template import Template, Context
from django.template import loader
from django.shortcuts import render

# Create your views here.

def inicio(request):

    return render(request,'Despachador/inicio.html')

def paquetes(request):

    return render(request,'Despachador/paquetes.html')

def conductores(request):

    return render(request,'Despachador/conductores.html')