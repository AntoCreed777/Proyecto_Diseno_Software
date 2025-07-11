from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from api.models import Usuario, Cliente
from django.contrib.auth.models import Group
from django.db import transaction
from api.models import Usuario, TiposRoles
from api.exceptions import GroupNotConfiguredError
from captcha.fields import CaptchaField
class RegistroClienteForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")
    first_name = forms.CharField(required=True, label="Nombre", max_length=30)
    last_name = forms.CharField(required=True, label="Apellidos", max_length=30)
    telefono = forms.CharField(required=False, label="Teléfono")
    direccion_hogar = forms.CharField(required=False, label="Dirección del hogar")

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 'direccion_hogar', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, placeholder in {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono (opcional)',
            'direccion_hogar': 'Dirección de su residencia (opcional)',
            'password1': 'Contraseña',
            'password2': 'Confirma tu contraseña',
        }.items():
            self.fields[field_name].widget.attrs.update({'class': 'form-control', 'placeholder': placeholder})
    
    def clean_email(self):
        email = str(self.cleaned_data.get('email')).strip()
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("El correo electrónico ya está registrado.")
        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email'].strip()
        usuario.first_name = self.cleaned_data['first_name'].strip()
        usuario.last_name = self.cleaned_data['last_name'].strip()
        usuario.telefono = self.cleaned_data['telefono'].strip()
        usuario.rol = TiposRoles.CLIENTE
        if commit:
            with transaction.atomic():
                usuario.save()

                try:
                    grupo = Group.objects.get(name=TiposRoles.CLIENTE)
                except Group.DoesNotExist:
                    raise GroupNotConfiguredError(f"El grupo '{TiposRoles.CLIENTE}' no está configurado en la base de datos.")

                usuario.groups.add(grupo)

                Cliente.objects.create(
                    usuario=usuario, 
                    direccion_hogar=self.cleaned_data['direccion_hogar'].strip()
                )
        return usuario

class CustomLoginForm(AuthenticationForm):
    captcha = CaptchaField()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, placeholder in {
            'username': 'Nombre de usuario',
            'password': 'Contraseña',
        }.items():
            self.fields[field_name].widget.attrs.update({'class': 'form-control', 'placeholder': placeholder})
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        user = Usuario.objects.filter(username=username).first()

        if user and not user.email_verified:
            raise forms.ValidationError(
                "Tu correo electrónico no ha sido verificado. Por favor, revisa tu bandeja de entrada.",
                code='email_not_verified',
            )
        
        return cleaned_data
