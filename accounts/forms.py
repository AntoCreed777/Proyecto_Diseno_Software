from django import forms
from django.contrib.auth.forms import UserCreationForm
from api.models import Usuario, Cliente
from django.contrib.auth.models import Group
from django.db import transaction
from api.models import Usuario

class RegistroClienteForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")
    telefono = forms.CharField(required=False, label="Teléfono")
    direccion_hogar = forms.CharField(required=False, label="Dirección del hogar")

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'telefono', 'direccion_hogar', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, placeholder in {
            'username': 'Nombre de usuario',
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
        usuario.telefono = self.cleaned_data['telefono'].strip()
        usuario.rol = 'cliente'
        if commit:
            with transaction.atomic():
                usuario.save()

                try:
                    grupo = Group.objects.get(name='Cliente')
                except Group.DoesNotExist:
                    raise ValueError("El grupo 'Cliente' no está configurado en la base de datos.")

                usuario.groups.add(grupo)

                Cliente.objects.create(
                    usuario=usuario, 
                    direccion_hogar=self.cleaned_data['direccion_hogar'].strip()
                )
        return usuario
