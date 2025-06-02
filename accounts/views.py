from django.shortcuts import render, redirect
from django.http import HttpResponse
from api.models import Usuario     # Usuario Custom de Django
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db import IntegrityError

# Create your views here.
source='html'
def login_view(request):
     if request.method == 'POST':
          usuario = request.POST.get('usuario', '')
          contraseña = request.POST.get('contraseña', '')
          user = authenticate(request, username=usuario, password=contraseña)
          if user is None:
               messages.error(request, 'Usuario o contraseña son incorrectos')
          else:
               login(request, user)
               
               # Redirigir según el rol del usuario
               if user.rol == 'admin':  
                    return redirect('/admin/dashboard')
               elif user.rol == 'conductor':
                    return redirect('/conductor/inicio')
               else:
                    return redirect('/home/main')

     return render(request, 'login.html')

def registration(request):
     if request.method == 'POST':
          if request.POST.get('usuario', '') is None:
               messages.error(request, 'Ingrese un nombre de usuario')

          elif request.POST['contraseña'] == request.POST['contraseña2']:
               try:
                    usuario = request.POST.get('usuario', '')
                    contraseña = request.POST.get('contraseña', '')
                    user = Usuario.objects.create_user(username=usuario, password=contraseña)
                    user.save()
                    return redirect('/accounts/login')
               except IntegrityError:
                    messages.error(request, 'El usuario ya existe')
          else:
               messages.error(request, 'Las contraseñas no coinciden')
     
     return render(request, 'registration.html')