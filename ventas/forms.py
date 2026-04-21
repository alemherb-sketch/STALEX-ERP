from django import forms
from django.forms import inlineformset_factory
from .models import Cotizacion, CotizacionDetalle, OrdenPedido, OrdenPedidoDetalle

class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['fecha', 'cliente', 'notas']
        widgets = {
            'fecha': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CotizacionDetalleForm(forms.ModelForm):
    class Meta:
        model = CotizacionDetalle
        fields = ['producto', 'presentacion', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control product-select'}),
            'presentacion': forms.Select(attrs={'class': 'form-control presentation-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

CotizacionDetalleFormSet = inlineformset_factory(
    Cotizacion, CotizacionDetalle, form=CotizacionDetalleForm,
    extra=1, can_delete=True
)

class OrdenPedidoForm(forms.ModelForm):
    class Meta:
        model = OrdenPedido
        fields = ['fecha', 'cliente', 'cotizacion_referencia']
        widgets = {
            'fecha': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'cotizacion_referencia': forms.Select(attrs={'class': 'form-control'}),
        }

class OrdenPedidoDetalleForm(forms.ModelForm):
    class Meta:
        model = OrdenPedidoDetalle
        fields = ['producto', 'presentacion', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control product-select'}),
            'presentacion': forms.Select(attrs={'class': 'form-control presentation-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

OrdenPedidoDetalleFormSet = inlineformset_factory(
    OrdenPedido, OrdenPedidoDetalle, form=OrdenPedidoDetalleForm,
    extra=1, can_delete=True
)
