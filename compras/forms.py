from django import forms
from django.forms import inlineformset_factory
from .models import OrdenCompra, OrdenCompraDetalle

class OrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = ['fecha', 'proveedor', 'notas']
        widgets = {
            'fecha': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class OrdenCompraDetalleForm(forms.ModelForm):
    class Meta:
        model = OrdenCompraDetalle
        fields = ['producto', 'presentacion', 'cantidad', 'costo_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control product-select'}),
            'presentacion': forms.Select(attrs={'class': 'form-control presentation-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'costo_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

OrdenCompraDetalleFormSet = inlineformset_factory(
    OrdenCompra, OrdenCompraDetalle, form=OrdenCompraDetalleForm,
    extra=1, can_delete=True
)
