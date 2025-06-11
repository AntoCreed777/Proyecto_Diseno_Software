from django.urls import path
from .views import inicio, paquetes, rendimiento

app_name = 'conductor'
urlpatterns = [
    path('inicio/', inicio, name = 'inicio'),
    path('paquetes/', paquetes, name = 'paquetes'),
    path('rendimiento/', rendimiento, name = 'rendimiento'),
]
