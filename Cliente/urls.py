from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name = 'inicio'),
    path('mis_pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('ayuda/', views.ayuda, name='ayuda'),
]
