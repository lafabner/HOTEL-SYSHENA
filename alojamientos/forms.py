from django import forms

from .models import Alojamiento


class AlojamientoForm(forms.ModelForm):
    """Datos editables del alojamiento en la pantalla Configuración."""

    class Meta:
        model = Alojamiento
        fields = ['nombre', 'municipio', 'direccion', 'telefono', 'correo', 'descripcion',
                  'informacion_turistica', 'hora_checkin', 'hora_checkout']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'municipio': forms.Select(attrs={'class': 'form-select'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'informacion_turistica': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'hora_checkin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_checkout': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
        labels = {
            'hora_checkin': 'Hora de check-in',
            'hora_checkout': 'Hora de check-out',
        }
