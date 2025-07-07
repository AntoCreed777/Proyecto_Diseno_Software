from django.urls import path
from . import views

urlpatterns = [
    path('inicio/', views.inicio, name = 'inicio_cliente'),
    path('mis_paquetes/', views.mis_paquetes, name='mis_paquetes'),
    path('ayuda/', views.ayuda, name='ayuda'),
]
