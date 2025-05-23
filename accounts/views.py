from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib import messages

# Create your views here.
def login_view(request):
     if request.method == 'POST':
          user = authenticate(request,username=request.POST['usuario'],password=request.POST['contraseña'])
          if user is None:
                messages.error(request, 'Usuario o contraseña incorrectos')
          else:
               login(request,user)
               return redirect('map')
     return render(request, 'login.html')
     
def registration(request):
     if request.method == 'POST':
          try:
               user = User.objects.create_user(username=request.POST['usuario'],password=request.POST['contraseña'])
               user.save()
               return HttpResponse('Usuario creado')
          except:
               return HttpResponse('Fallo')
     return render(request, 'registration.html')