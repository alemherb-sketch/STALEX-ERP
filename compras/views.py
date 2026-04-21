from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, permission_required
from .models import OrdenCompra, OrdenCompraDetalle
from .forms import OrdenCompraForm, OrdenCompraDetalleFormSet
from inventario.models import Almacen, Stock, Kardex, Producto
from decimal import Decimal
import datetime
import random
import json

class OrdenCompraListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = OrdenCompra
    template_name = 'compras/orden_compra_list.html'
    context_object_name = 'ordenes'
    permission_required = 'compras.view_ordencompra'

class OrdenCompraCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = OrdenCompra
    form_class = OrdenCompraForm
    template_name = 'compras/orden_compra_form.html'
    success_url = reverse_lazy('compras:orden_compra_list')
    permission_required = 'compras.add_ordencompra'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['detalles'] = OrdenCompraDetalleFormSet(self.request.POST)
        else:
            data['detalles'] = OrdenCompraDetalleFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        
        form.instance.numero = f"OC-{datetime.date.today().year}-{random.randint(1000, 9999)}"
        
        if detalles.is_valid():
            self.object = form.save()
            detalles.instance = self.object
            instances = detalles.save(commit=False)
            subtotal_total = 0
            for instance in instances:
                instance.subtotal = instance.cantidad * instance.costo_unitario
                instance.save()
                subtotal_total += instance.subtotal
            
            self.object.subtotal = subtotal_total
            self.object.igv = subtotal_total * Decimal('0.18')
            self.object.total = subtotal_total * Decimal('1.18')
            self.object.save()
            
            messages.success(self.request, "Orden de Compra generada exitosamente.")
            return redirect('compras:orden_compra_print', pk=self.object.pk)
        else:
            return self.form_invalid(form)

class OrdenCompraPrintView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = OrdenCompra
    template_name = 'compras/orden_compra_print.html'
    context_object_name = 'orden'
    permission_required = 'compras.view_ordencompra'

class OrdenCompraUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = OrdenCompra
    form_class = OrdenCompraForm
    template_name = 'compras/orden_compra_form.html'
    success_url = reverse_lazy('compras:orden_compra_list')
    permission_required = 'compras.change_ordencompra'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['detalles'] = OrdenCompraDetalleFormSet(self.request.POST, instance=self.object)
        else:
            data['detalles'] = OrdenCompraDetalleFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        
        if detalles.is_valid():
            self.object = form.save()
            detalles.instance = self.object
            instances = detalles.save(commit=False)
            
            for obj in detalles.deleted_objects:
                obj.delete()
                
            for instance in instances:
                instance.subtotal = instance.cantidad * instance.costo_unitario
                instance.save()
            
            subtotal_total = sum(d.subtotal for d in self.object.detalles.all())
            self.object.subtotal = subtotal_total
            self.object.igv = subtotal_total * Decimal('0.18')
            self.object.total = subtotal_total * Decimal('1.18')
            self.object.save()
            
            messages.success(self.request, "Orden de Compra actualizada.")
            return redirect('compras:orden_compra_list')
        else:
            return self.form_invalid(form)

class OrdenCompraDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = OrdenCompra
    template_name = 'compras/orden_compra_confirm_delete.html'
    success_url = reverse_lazy('compras:orden_compra_list')
    permission_required = 'compras.delete_ordencompra'

@login_required
@permission_required('compras.change_ordencompra', raise_exception=True)
def recibir_orden_compra(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    if orden.estado == 'RECIBIDA':
        messages.warning(request, "Esta orden ya fue recibida anteriormente.")
        return redirect('compras:orden_compra_list')
        
    almacenes = Almacen.objects.all()
    
    if request.method == 'POST':
        almacen_id = request.POST.get('almacen')
        almacen = get_object_or_404(Almacen, pk=almacen_id)
        
        # Incrementar stock y generar Kardex
        for detalle in orden.detalles.all():
            # Multiplicador por presentación
            multiplier = detalle.presentacion.cantidad_por_paquete if detalle.presentacion else 1
            cantidad_fisica = Decimal(str(detalle.cantidad)) * Decimal(str(multiplier))
            
            stock, _ = Stock.objects.get_or_create(producto=detalle.producto, almacen=almacen)
            stock.cantidad = Decimal(str(stock.cantidad)) + cantidad_fisica
            stock.save()
            
            Kardex.objects.create(
                producto=detalle.producto,
                almacen=almacen,
                tipo_movimiento='ENTRADA',
                cantidad=cantidad_fisica,
                saldo_actual=stock.cantidad,
                motivo=f'Compra (Recibida O.C. {orden.numero})',
                referencia=orden.numero
            )
            
            # Actualizar último costo del producto opcionalmente
            producto = detalle.producto
            producto.costo = detalle.costo_unitario / Decimal(str(multiplier))
            producto.save()
            
        orden.estado = 'RECIBIDA'
        orden.save()
        
        messages.success(request, f"Orden de Compra {orden.numero} recibida en almacén {almacen.nombre}. Stock actualizado.")
        return redirect('compras:orden_compra_list')
        
    return render(request, 'compras/orden_compra_recibir.html', {'orden': orden, 'almacenes': almacenes})
