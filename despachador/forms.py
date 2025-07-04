from django import forms
from api.models import Paquete, Cliente, Despachador
from maps.utilities import obtener_coordenadas
from geopy.exc import GeocoderTimedOut
import re

class RegistroPaqueteForm(forms.ModelForm):
    dimensiones = forms.CharField(
        max_length=50,
        label="Dimensiones (largo x ancho x alto)",
        help_text="Formato: 10x20x30 (en centímetros)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ejemplo: 10x20x30'})
    )
    
    class Meta:
        model = Paquete
        fields = [
            'cliente', 'nombre_destinatario', 'rut_destinatario', 
            'telefono_destinatario', 'direccion_envio_texto', 'peso'
        ]
        labels = {
            'cliente': 'Cliente',
            'nombre_destinatario': 'Nombre del destinatario',
            'rut_destinatario': 'RUT del destinatario',
            'telefono_destinatario': 'Teléfono del destinatario',
            'direccion_envio_texto': 'Dirección de envío',
            'peso': 'Peso (kg)',
        }
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'nombre_destinatario': forms.TextInput(attrs={'class': 'form-control'}),
            'rut_destinatario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.345.678-9'}),
            'telefono_destinatario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'direccion_envio_texto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle, número, comuna, ciudad'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'min': '0.01', 'placeholder': '0.0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.select_related('usuario').all()
        self.fields['cliente'].empty_label = "Seleccione un cliente"

    def clean_dimensiones(self):
        dimensiones = self.cleaned_data.get('dimensiones', '').strip()
        
        # Patrón regex para validar formato: número x número x número
        patron = r'^\d+(\.\d+)?\s*x\s*\d+(\.\d+)?\s*x\s*\d+(\.\d+)?$'
        
        if not re.match(patron, dimensiones):
            raise forms.ValidationError("Las dimensiones deben tener el formato: largo x ancho x alto (ejemplo: 10x20x30)")
        
        # Extraer las dimensiones
        partes = [float(x.strip()) for x in dimensiones.split('x')]
        largo, ancho, alto = partes
        
        # Validar que todas las dimensiones sean positivas
        if any(dim <= 0 for dim in [largo, ancho, alto]):
            raise forms.ValidationError("Todas las dimensiones deben ser mayores a 0")
        
        return dimensiones

    def clean_rut_destinatario(self):
        rut = self.cleaned_data.get('rut_destinatario', '').strip()
        
        # Validación básica de formato RUT chileno
        patron_rut = r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$'
        
        if not re.match(patron_rut, rut):
            raise forms.ValidationError("El RUT debe tener el formato: 12.345.678-9")
        
        return rut

    def clean_telefono_destinatario(self):
        telefono = self.cleaned_data.get('telefono_destinatario', '')
        telefono_str = str(telefono).strip()
        
        # Validación básica de teléfono chileno
        if not telefono_str.startswith('+56'):
            raise forms.ValidationError("El teléfono debe comenzar con +56")
        
        return telefono

    def save(self, commit=True, despachador=None, skip_coordinates=False):
        paquete = super().save(commit=False)
        
        # Procesar dimensiones
        dimensiones = self.cleaned_data['dimensiones']
        partes = [float(x.strip()) for x in dimensiones.split('x')]
        paquete.largo, paquete.ancho, paquete.alto = partes
        
        # Asignar despachador
        if despachador:
            paquete.despachador = despachador
        
        # Obtener coordenadas de la dirección de envío solo si no se van a confirmar manualmente
        if not skip_coordinates:
            direccion = self.cleaned_data['direccion_envio_texto']
            try:
                coordenadas = obtener_coordenadas(direccion)
                if coordenadas:
                    paquete.direccion_envio_lat = coordenadas[0]
                    paquete.direccion_envio_lng = coordenadas[1]
                else:
                    # Usar coordenadas por defecto si no se pueden obtener
                    paquete.direccion_envio_lat = -36.8485
                    paquete.direccion_envio_lng = -73.0324
            except GeocoderTimedOut:
                # Usar coordenadas por defecto en caso de timeout
                paquete.direccion_envio_lat = -36.8485
                paquete.direccion_envio_lng = -73.0324
            except Exception:
                # Usar coordenadas por defecto para cualquier otro error
                paquete.direccion_envio_lat = -36.8485
                paquete.direccion_envio_lng = -73.0324
        
        if commit:
            paquete.save()
        
        return paquete
