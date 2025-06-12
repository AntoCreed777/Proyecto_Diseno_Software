from django.urls import path
from . import views

urlpatterns = [
    path('inicio/', views.inicio, name = 'inicio_cliente'),
    path('mis_pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('ayuda/', views.ayuda, name='ayuda'),
]
