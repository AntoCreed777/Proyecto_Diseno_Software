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
                    return redirect('/home/')

     return render(request, 'login.html')

def registration(request):
     if request.method == 'POST':
          usuario = request.POST.get('usuario', '')
          contraseña = request.POST.get('contraseña','')
          contraseña2 = request.POST.get('contraseña2','')
          correo = request.POST.get('email','')
          numero = request.POST.get('telefono','')
          if usuario is None:
               messages.error(request, 'Ingrese un nombre de usuario')
          elif " " in contraseña:
               messages.error(request,"No se admiten espacios en la contraseña")
          
          elif contraseña == contraseña2:
               try:
                    user = Usuario.objects.create_user(username=usuario, password=contraseña,email=correo,telefono=numero)
                    user.save()
                    return redirect('/accounts/login')
               except IntegrityError:
                    messages.error(request, 'El usuario ya existe')
               except Exception as e:
                    messages.error(request, 'Ocurrió un error inesperado')
          else:
               messages.error(request, 'Las contraseñas no coinciden')
     
     return render(request, 'registration.html')