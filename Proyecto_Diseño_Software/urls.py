"""
URL configuration for Proyecto_Diseño_Software project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),  # URL para el panel de administración
    path('', RedirectView.as_view(url='/home/', permanent=True)),  # Redirige la raíz a /home
    path('maps/', include('maps.urls')),  # Incluye las URLs de la app de mapas
    path('accounts/', include('accounts.urls')),  # Incluye las URLs de la app de cuentas
    path('api/', include('api.urls')),  # Incluye las URLs de la API de la BD
    path('home/',include('home.urls')),
    path('conductor/', include('Conductor.urls')), # Incluye URLs de la página conductor
    path('administrador/', include('Administrador.urls')), # Incluye URLs de la página administrador
    path('despachador/', include('despachador.urls')),  # Incluye URLs de la página despachador
    path('cliente/', include('Cliente.urls')), # Incluye URLs de la página cliente
]
