from django import forms
from django.forms import inlineformset_factory
from .models import Producto, Almacen, PresentacionProducto, MovimientoAlmacen, MovimientoAlmacenDetalle

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'descripcion', 'categoria', 'precio_venta', 'costo', 'peso', 'unidad_medida']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'costo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Kg'}),
            'unidad_medida': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProductoForm, self).__init__(*args, **kwargs)
        if self.user and not self.user.has_perm('inventario.can_view_price'):
            self.fields.pop('precio_venta', None)
            self.fields.pop('costo', None)

class PresentacionProductoForm(forms.ModelForm):
    class Meta:
        model = PresentacionProducto
        fields = ['nombre', 'cantidad_por_paquete', 'precio_paquete']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Paquete x6'}),
            'cantidad_por_paquete': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_paquete': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

PresentacionFormSet = inlineformset_factory(
    Producto, PresentacionProducto, form=PresentacionProductoForm,
    extra=1, can_delete=True
)

class AlmacenForm(forms.ModelForm):
    class Meta:
        model = Almacen
        fields = ['nombre', 'ubicacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MovimientoAlmacenForm(forms.ModelForm):
    class Meta:
        model = MovimientoAlmacen
        fields = ['tipo', 'almacen', 'motivo', 'referencia']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'almacen': forms.Select(attrs={'class': 'form-control'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Ajuste de inventario'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
        }

class MovimientoAlmacenDetalleForm(forms.ModelForm):
    class Meta:
        model = MovimientoAlmacenDetalle
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

MovimientoAlmacenDetalleFormSet = inlineformset_factory(
    MovimientoAlmacen, MovimientoAlmacenDetalle, form=MovimientoAlmacenDetalleForm,
    extra=1, can_delete=True
)
