from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User,Group
from django.contrib.auth import authenticate,login
from django.contrib import messages
from django.db import IntegrityError
# Create your views here.
def login_view(request):
     if request.method == 'POST':
          user = authenticate(request,username=request.POST['usuario'],password=request.POST['contraseña'])
          if user is None:
                messages.error(request, 'Usuario o contraseña incorrectos')
          else:
               login(request,user)
               return redirect('/home/main')
     return render(request, 'login.html')
     
def registration(request):
     if request.method == 'POST':
          if(request.POST['contraseña'] == request.POST['contraseña2']):
               try:
                    user = User.objects.create_user(username=request.POST['usuario'],password=request.POST['contraseña'])
                    grupo = Group.objects.get(name='usuarios')
                    user.groups.add(grupo)
                    user.save()
                    return redirect('/accounts/login')
               except IntegrityError:
                    messages.error(request,'El usuario ya existe')
          else:
               messages.error(request,'Las constraseñas no coinciden')
          
     return render(request, 'registration.html')