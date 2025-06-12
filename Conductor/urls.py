from django.urls import path
from .views import inicio, paquetes, rendimiento, cambiar_estado_paquete_conductor

app_name = 'conductor'
urlpatterns = [
    path('inicio/', inicio, name = 'inicio_conductor'),
    path('paquetes/', paquetes, name = 'paquetes'),
    path('rendimiento/', rendimiento, name = 'rendimiento'),
    path('cambiar-estado/', cambiar_estado_paquete_conductor, name='cambiar_estado_paquete_conductor'),
]
