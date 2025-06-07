from django.shortcuts import render, redirect
from django.http import HttpResponse
from api.models import Usuario     # Usuario Custom de Django
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db import IntegrityError
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from api.serializers import UsuarioSerializer, ClienteSerializer
from django.db import transaction
from .forms import RegistroClienteForm

#Activacion del correo
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Gracias, por activar su cuenta.')
        return redirect('login')
    else:
        messages.error(request, 'La activacion fallo')
    
    return redirect('login')

#Envia el correo
def activarEmail(request,user,correo):
     #sujeto del correo
     mail_subject = 'Activar tu cuenta.'
     #link del correo
     message = render_to_string('activar_cuenta.html', {
        'user': user.username,
        'dominio': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocolo': 'https' if request.is_secure() else 'http'
    })
     email = EmailMessage(mail_subject,message,to=[correo])
     if email.send():
          messages.success(request,f"Por favor {user} verifique su correo electronico {correo}")
     else:
          messages.success(request,"Ocurrio un error")

def login_view(request):
     if request.method == 'POST':
          usuario = request.POST.get('usuario', '')
          contraseña = request.POST.get('contraseña', '')
          user = authenticate(request, username=usuario, password=contraseña)
          if user is None:
               messages.error(request, 'Usuario o contraseña son incorrectos')
          elif not user.is_active:
               messages.error(request, 'Por favor, para continuar debe activar su cuenta, ingresando a su correo electronico')
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
          form = RegistroClienteForm(request.POST)
          if form.is_valid():
               form.save()
               messages.success(request, 'Registro exitoso. Por favor, inicie sesión.')
               return redirect('/accounts/login')
     else:
          form = RegistroClienteForm()

     return render(request, 'registration.html', {'form': form})