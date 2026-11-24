from django import forms
from django.utils import timezone

from huespedes.models import Huesped
from usuarios.forms import ATTRS_NUMERICOS, validar_solo_digitos
from .models import Reserva


class HuespedReservaForm(forms.ModelForm):
    """Datos del huésped. Si el usuario logueado es cliente y ya existe,
    los campos quedan bloqueados."""

    class Meta:
        model = Huesped
        fields = ['tipo_documento', 'numero_documento', 'nombres', 'apellidos',
                  'telefono', 'correo', 'nacionalidad']
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(
                attrs={'class': 'form-control', **ATTRS_NUMERICOS}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(
                attrs={'class': 'form-control', **ATTRS_NUMERICOS}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, huesped_actual=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.huesped_actual = huesped_actual
        if huesped_actual is not None:
            for campo in self.fields:
                self.fields[campo].disabled = True
                self.initial[campo] = getattr(huesped_actual, campo)

    def clean_numero_documento(self):
        if self.huesped_actual is not None:
            return self.huesped_actual.numero_documento
        doc = validar_solo_digitos('número de documento',
                                   self.cleaned_data.get('numero_documento'))
        if doc:
            existe = Huesped.objects.filter(
                tipo_documento=self.data.get('tipo_documento'), numero_documento=doc).exists()
            if existe:
                raise forms.ValidationError('Ya existe un huésped con ese documento.')
        return doc

    def clean_telefono(self):
        if self.huesped_actual is not None:
            return self.huesped_actual.telefono
        return validar_solo_digitos('teléfono', self.cleaned_data.get('telefono'),
                                    minimo=7, maximo=15)


class EstadiaForm(forms.Form):
    fecha_entrada = forms.DateField(
        label='Entrada',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    fecha_salida = forms.DateField(
        label='Salida',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    numero_huespedes = forms.IntegerField(
        label='Número de huéspedes', min_value=1,
        widget=forms.NumberInput(attrs={'type': 'number', 'class': 'form-control'}))
    habitacion = forms.ModelChoiceField(
        label='Habitación', queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}))
    observaciones = forms.CharField(
        label='Observaciones', required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                     'placeholder': 'Información adicional de la reserva'}))

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario
        if self.data:                       # ya hay datos: muestra solo las libres
            self.fields['habitacion'].queryset = self._disponibles_o_todas()
        else:                                # primera carga: todas las activas
            from habitaciones.models import Habitacion
            self.fields['habitacion'].queryset = Habitacion.objects.filter(activa=True)

    def _disponibles_o_todas(self):
        """Filtra las habitaciones disponibles, pero sin reventar si las
        fechas aún están mal. En ese caso muestra todas las activas."""
        from habitaciones.models import Habitacion
        try:
            d = {
                'fecha_entrada': self.fields['fecha_entrada'].clean(self.data.get('fecha_entrada')),
                'fecha_salida': self.fields['fecha_salida'].clean(self.data.get('fecha_salida')),
                'numero_huespedes': self.fields['numero_huespedes'].clean(self.data.get('numero_huespedes')),
            }
        except Exception:
            return Habitacion.objects.filter(activa=True)
        try:
            from reservas import logica as rl
            return rl.habitaciones_disponibles(d['fecha_entrada'], d['fecha_salida'],
                                               d['numero_huespedes'])
        except Exception:
            return Habitacion.objects.filter(activa=True)

    def clean(self):
        datos = super().clean()
        entrada = datos.get('fecha_entrada')
        salida = datos.get('fecha_salida')
        huespedes = datos.get('numero_huespedes')
        habitacion = datos.get('habitacion')
        if entrada and salida and salida <= entrada:
            self.add_error('fecha_salida',
                           'La fecha de salida debe ser posterior a la fecha de entrada.')
        if entrada and entrada < timezone.localdate():
            self.add_error('fecha_entrada',
                           'La fecha de entrada no puede estar en el pasado.')
        if habitacion and huespedes and huespedes > habitacion.capacidad:
            self.add_error('numero_huespedes',
                           f'Supera la capacidad de la habitación ({habitacion.capacidad}).')
        return datos

    def resumen(self):
        """Calcula lo que muestra la tarjeta Resumen antes de guardar."""
        from decimal import Decimal
        d = self.cleaned_data
        habitacion = d['habitacion']
        noches = (d['fecha_salida'] - d['fecha_entrada']).days
        total = habitacion.precio_noche * noches
        return {
            'habitacion': habitacion,
            'noches': noches,
            'total': total,
            'servicios': Decimal('0'),
        }
