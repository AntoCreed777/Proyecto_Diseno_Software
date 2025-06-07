from http.client import HTTPResponse

from django.shortcuts import render

# Create your views here.
def inicio(request):

    return render(request,'Cliente/inicio.html')

def mis_pedidos(request):

    return render(request,'Cliente/mis_pedidos.html')

def ayuda(request):

    return render(request,'Cliente/ayuda.html')