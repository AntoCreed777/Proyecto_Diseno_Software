from django.urls import path
from .views import inicio, paquetes, rendimiento

urlpatterns = [
    path('inicio/', inicio, name = 'inicio'),
    path('paquetes/', paquetes, name = 'paquetes'),
    path('rendimiento/', rendimiento, name = 'rendimiento'),
]
