from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from .models import Producto, Almacen, Kardex, Stock, MovimientoAlmacen, PresentacionProducto
from .forms import ProductoForm, AlmacenForm, PresentacionFormSet, MovimientoAlmacenForm, MovimientoAlmacenDetalleFormSet

# PRODUCTOS
class ProductoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Producto
    template_name = 'inventario/producto_list.html'
    context_object_name = 'productos'
    permission_required = 'inventario.view_producto'

class ProductoCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto_form.html'
    success_url = reverse_lazy('inventario:producto_list')
    success_message = "Producto creado exitosamente."
    permission_required = 'inventario.add_producto'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['presentaciones'] = PresentacionFormSet(self.request.POST)
        else:
            data['presentaciones'] = PresentacionFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        presentaciones = context['presentaciones']
        producto = form.save(commit=False)
        if not getattr(producto, 'precio_venta', None) and 'precio_venta' not in form.fields:
            producto.precio_venta = 0.00
        if not getattr(producto, 'costo', None) and 'costo' not in form.fields:
            producto.costo = 0.00
        producto.save()
        if presentaciones.is_valid():
            presentaciones.instance = producto
            presentaciones.save()
        return super().form_valid(form)

class ProductoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto_form.html'
    success_url = reverse_lazy('inventario:producto_list')
    success_message = "Producto actualizado exitosamente."
    permission_required = 'inventario.change_producto'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['presentaciones'] = PresentacionFormSet(self.request.POST, instance=self.object)
        else:
            data['presentaciones'] = PresentacionFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        presentaciones = context['presentaciones']
        producto = form.save(commit=False)
        if not getattr(producto, 'precio_venta', None) and 'precio_venta' not in form.fields:
            producto.precio_venta = 0.00
        if not getattr(producto, 'costo', None) and 'costo' not in form.fields:
            producto.costo = 0.00
        producto.save()
        if presentaciones.is_valid():
            presentaciones.instance = producto
            presentaciones.save()
        return super().form_valid(form)

class ProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Producto
    template_name = 'inventario/producto_confirm_delete.html'
    success_url = reverse_lazy('inventario:producto_list')
    permission_required = 'inventario.delete_producto'

# ALMACENES
class AlmacenListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Almacen
    template_name = 'inventario/almacen_list.html'
    context_object_name = 'almacenes'
    permission_required = 'inventario.view_almacen'

class AlmacenCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Almacen
    form_class = AlmacenForm
    template_name = 'inventario/almacen_form.html'
    success_url = reverse_lazy('inventario:almacen_list')
    success_message = "Almacén creado exitosamente."
    permission_required = 'inventario.add_almacen'

class AlmacenUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Almacen
    form_class = AlmacenForm
    template_name = 'inventario/almacen_form.html'
    success_url = reverse_lazy('inventario:almacen_list')
    success_message = "Almacén actualizado exitosamente."
    permission_required = 'inventario.change_almacen'

class AlmacenDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Almacen
    template_name = 'inventario/almacen_confirm_delete.html'
    success_url = reverse_lazy('inventario:almacen_list')
    permission_required = 'inventario.delete_almacen'

# KARDEX
class KardexListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Kardex
    template_name = 'inventario/kardex_list.html'
    context_object_name = 'kardex_records'
    paginate_by = 50
    permission_required = 'inventario.view_kardex'

def get_product_details(request, product_id):
    producto = get_object_or_404(Producto, pk=product_id)
    presentaciones = producto.presentaciones.all()
    
    data = {
        'precio_venta': float(producto.precio_venta),
        'presentaciones': [
            {
                'id': p.id,
                'nombre': p.nombre,
                'cantidad': float(p.cantidad_por_paquete),
                'precio_paquete': float(p.precio_paquete),
                'precio_unitario': float(p.precio_unitario)
            } for p in presentaciones
        ]
    }
    return JsonResponse(data)

# MOVIMIENTOS MANUALES DE ALMACEN
class MovimientoAlmacenListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = MovimientoAlmacen
    template_name = 'inventario/movimiento_almacen_list.html'
    context_object_name = 'movimientos'
    permission_required = 'inventario.view_movimientoalmacen'

class MovimientoAlmacenCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = MovimientoAlmacen
    form_class = MovimientoAlmacenForm
    template_name = 'inventario/movimiento_almacen_form.html'
    success_url = reverse_lazy('inventario:movimiento_almacen_list')
    permission_required = 'inventario.add_movimientoalmacen'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['detalles'] = MovimientoAlmacenDetalleFormSet(self.request.POST)
        else:
            data['detalles'] = MovimientoAlmacenDetalleFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        if detalles.is_valid():
            self.object = form.save()
            detalles.instance = self.object
            instances = detalles.save()
            
            almacen = self.object.almacen
            tipo = self.object.tipo
            
            # Actualizar stock y Kardex por cada ítem
            for item in instances:
                stock, _ = Stock.objects.get_or_create(producto=item.producto, almacen=almacen)
                
                if tipo == 'ENTRADA':
                    stock.cantidad = Decimal(str(stock.cantidad)) + Decimal(str(item.cantidad))
                else:
                    stock.cantidad = Decimal(str(stock.cantidad)) - Decimal(str(item.cantidad))
                
                stock.save()
                
                Kardex.objects.create(
                    producto=item.producto,
                    almacen=almacen,
                    tipo_movimiento=tipo,
                    cantidad=item.cantidad,
                    saldo_actual=stock.cantidad,
                    motivo=f"Mov. Manual: {self.object.motivo}",
                    referencia=self.object.referencia
                )
            
            messages.success(self.request, "Movimiento de almacén registrado correctamente.")
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)

# RESUMEN DE STOCK
class StockSummaryView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Producto
    template_name = 'inventario/stock_list.html'
    context_object_name = 'productos'
    permission_required = 'inventario.view_stock'

    def get_queryset(self):
        # Anotamos el stock total sumando todas las cantidades en distintos almacenes
        return Producto.objects.annotate(stock_total=Sum('stocks__cantidad')).order_by('nombre')

