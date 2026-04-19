from django import forms
from django.forms import inlineformset_factory
from .models import OrdenDespacho, OrdenDespachoDetalle

class OrdenDespachoForm(forms.ModelForm):
    class Meta:
        model = OrdenDespacho
        fields = ['fecha', 'transportista', 'direccion_origen', 'direccion_destino']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'transportista': forms.Select(attrs={'class': 'form-control'}),
            'direccion_origen': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_destino': forms.TextInput(attrs={'class': 'form-control'}),
        }

class OrdenDespachoDetalleForm(forms.ModelForm):
    class Meta:
        model = OrdenDespachoDetalle
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

OrdenDespachoDetalleFormSet = inlineformset_factory(
    OrdenDespacho, OrdenDespachoDetalle, form=OrdenDespachoDetalleForm,
    extra=1, can_delete=True
)
