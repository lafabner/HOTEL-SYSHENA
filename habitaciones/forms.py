from django import forms

from .models import TipoHabitacion


class DisponibilidadForm(forms.Form):
    fecha_entrada = forms.DateField(
        label='Entrada',
        widget=forms.DateInput(attrs={'type': 'date', 'id': 'fIn', 'class': 'form-control'}))
    fecha_salida = forms.DateField(
        label='Salida',
        widget=forms.DateInput(attrs={'type': 'date', 'id': 'fOut', 'class': 'form-control'}))
    huespedes = forms.IntegerField(
        label='Huéspedes', min_value=1, initial=2,
        widget=forms.NumberInput(attrs={'id': 'people', 'class': 'form-control'}))
    tipo_habitacion = forms.ModelChoiceField(
        label='Tipo', queryset=TipoHabitacion.objects.filter(activo=True),
        empty_label='Todos', required=False,
        widget=forms.Select(attrs={'id': 'kind', 'class': 'form-select'}))

    def clean(self):
        datos = super().clean()
        entrada = datos.get('fecha_entrada')
        salida = datos.get('fecha_salida')
        if entrada and salida and salida <= entrada:
            raise forms.ValidationError('La fecha de salida debe ser posterior a la fecha de entrada.')
        return datos

    @property
    def noches(self):
        if self.is_valid() and 'fecha_entrada' in self.cleaned_data:
            return (self.cleaned_data['fecha_salida'] - self.cleaned_data['fecha_entrada']).days
        return 0
