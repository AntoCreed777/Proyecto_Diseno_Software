from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
# Create your views here.
def Temporal(request):
     return render(request, 'login.html')
def registration(request):
     if request.method == 'POST':
          try:
               user = User.objects.create_user(username=request.POST['usuario'],password=request.POST['contraseña'])
               return HttpResponse('Usuario creado')
          except:
               return HttpResponse('Fallo')
     return render(request, 'registration.html')