from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from .forms import RegistroClienteForm, CustomLoginForm
from api.models import TiposRoles

#Activacion del correo
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.email_verified = True
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
     if not email.send():
          messages.success(request,"Ocurrio un error al enviar el correo")

def login_view(request):
     if request.method == 'POST':
          form = CustomLoginForm(request, data=request.POST)
          if form.is_valid():
               user = form.get_user()
               login(request, user)

               if user.rol == TiposRoles.ADMIN:
                    return redirect('/admin/dashboard')
               elif user.rol == TiposRoles.CONDUCTOR:
                    return redirect('/conductor/inicio')
               elif user.rol == TiposRoles.DESPACHADOR:
                    return redirect('/despachador/inicio')
               elif user.rol == TiposRoles.CLIENTE:
                    return redirect('/cliente/inicio')
               else:
                    return redirect('/home/')
     else:
          form = CustomLoginForm()

     return render(request, 'login.html', {'form': form})

def registration(request):
     if request.method == 'POST':
          form = RegistroClienteForm(request.POST)
          if form.is_valid():
               usuario = form.save(commit=True)
               activarEmail(request, usuario, usuario.email)
               
               messages.success(request, 'Registro exitoso. Por favor, verifica tu correo para activar tu cuenta.')
               return redirect('/accounts/login')
     else:
          form = RegistroClienteForm()

     return render(request, 'registration.html', {'form': form})