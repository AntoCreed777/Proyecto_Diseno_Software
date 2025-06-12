from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .tokens import account_activation_token
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from .forms import RegistroClienteForm, CustomLoginForm
from api.models import TiposRoles
from django.conf import settings

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
def activarEmail(request, user):
     mail_subject = 'Activar tu cuenta.'

     message = render_to_string(
          'activar_cuenta.html',
          {
               'user': user.username,
               'dominio': get_current_site(request).domain,
               'uid': urlsafe_base64_encode(force_bytes(user.pk)),
               'token': account_activation_token.make_token(user),
               'protocolo': 'https' if request.is_secure() else 'http'
          }
     )
     email = EmailMessage(mail_subject,message,to=[user.email])
     if not email.send():
          messages.error(request,"Ocurrio un error al enviar el correo")

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
               activarEmail(request, usuario)
               
               messages.success(request, 'Registro exitoso. Por favor, verifica tu correo para activar tu cuenta.')
               return redirect('/accounts/login')
     else:
          form = RegistroClienteForm()

     return render(request, 'registration.html', {'form': form})
def notificar_cambio_estado_paquete(paquete):
    cliente = paquete.cliente
    usuario = cliente.usuario
    asunto = f"Actualización de estado de tu paquete #{paquete.id}"
    mensaje = (
        f"Hola {usuario.first_name},\n\n"
        f"El estado de tu paquete #{paquete.id} ha cambiado a: {paquete.get_estado_display()}.\n"
        f"Dirección de envío: {paquete.direccion_envio_texto}\n"
        f"Gracias por usar nuestro servicio."
    )
    destinatario = [usuario.email]
    send_mail(
        asunto,
        mensaje,
        settings.EMAIL_HOST_USER,
        destinatario,
        fail_silently=False,
    )