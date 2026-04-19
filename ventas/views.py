from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Cotizacion, OrdenPedido, CotizacionDetalle, OrdenPedidoDetalle
from .forms import CotizacionForm, CotizacionDetalleFormSet, OrdenPedidoForm, OrdenPedidoDetalleFormSet
from inventario.models import Almacen, Stock, Kardex, Producto
from decimal import Decimal
import random
import datetime
import json

# COTIZACIONES
class CotizacionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Cotizacion
    template_name = 'ventas/cotizacion_list.html'
    context_object_name = 'cotizaciones'
    permission_required = 'ventas.view_cotizacion'

class CotizacionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Cotizacion
    form_class = CotizacionForm
    template_name = 'ventas/cotizacion_form.html'
    success_url = reverse_lazy('ventas:cotizacion_list')
    permission_required = 'ventas.add_cotizacion'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['detalles'] = CotizacionDetalleFormSet(self.request.POST)
        else:
            data['detalles'] = CotizacionDetalleFormSet()
            
        productos = Producto.objects.all()
        prices = {str(p.id): float(p.precio_venta) for p in productos}
        data['product_prices'] = json.dumps(prices)
        
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        
        # Generar número de cotización temporal (Mock logic para MVP)
        form.instance.numero = f"COT-{datetime.date.today().year}-{random.randint(1000, 9999)}"
        
        if detalles.is_valid():
            self.object = form.save()
            detalles.instance = self.object
            instances = detalles.save(commit=False)
            subtotal_total = 0
            for instance in instances:
                instance.subtotal = instance.cantidad * instance.precio_unitario
                instance.save()
                subtotal_total += instance.subtotal
            
            self.object.subtotal = subtotal_total
            self.object.igv = float(subtotal_total) * 0.18
            self.object.total = float(subtotal_total) * 1.18
            self.object.save()
            
            messages.success(self.request, "Cotizacion generada. Procediendo a imprimir.")
            return redirect('ventas:cotizacion_print', pk=self.object.pk)
        else:
            return self.form_invalid(form)

class CotizacionPrintView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Cotizacion
    template_name = 'ventas/cotizacion_print.html'
    context_object_name = 'cotizacion'
    permission_required = 'ventas.view_cotizacion'

class CotizacionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Cotizacion
    form_class = CotizacionForm
    template_name = 'ventas/cotizacion_form.html'
    success_url = reverse_lazy('ventas:cotizacion_list')
    permission_required = 'ventas.change_cotizacion'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['detalles'] = CotizacionDetalleFormSet(self.request.POST, instance=self.object)
        else:
            data['detalles'] = CotizacionDetalleFormSet(instance=self.object)
            
        productos = Producto.objects.all()
        prices = {str(p.id): float(p.precio_venta) for p in productos}
        data['product_prices'] = json.dumps(prices)
        
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        
        if detalles.is_valid():
            self.object = form.save()
            detalles.instance = self.object
            instances = detalles.save(commit=False)
            
            # Remove deleted models
            for obj in detalles.deleted_objects:
                obj.delete()
                
            subtotal_total = 0
            for instance in instances:
                instance.subtotal = instance.cantidad * instance.precio_unitario
                instance.save()
            
            # Recalculate total iterating over all related objects because some might not have been modified but still exist
            for obj in self.object.detalles.all():
                subtotal_total += obj.subtotal
            
            self.object.subtotal = subtotal_total
            self.object.igv = float(subtotal_total) * 0.18
            self.object.total = float(subtotal_total) * 1.18
            self.object.save()
            
            messages.success(self.request, "Cotización actualizada exitosamente.")
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class CotizacionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Cotizacion
    template_name = 'ventas/cotizacion_confirm_delete.html'
    success_url = reverse_lazy('ventas:cotizacion_list')
    permission_required = 'ventas.delete_cotizacion'
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Cotización eliminada físicamente del sistema.")
        return super().delete(request, *args, **kwargs)

@login_required
@permission_required('ventas.change_cotizacion', raise_exception=True)
@require_POST
def cotizacion_anular(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    cotizacion.estado = 'ANULADA'
    cotizacion.save()
    messages.success(request, f"La Cotización {cotizacion.numero} ha sido ANULADA con éxito.")
    return redirect('ventas:cotizacion_list')

@login_required
@permission_required('ventas.add_ordenpedido', raise_exception=True)
@require_POST
def cotizacion_generar_pedido(request, pk):
    """Genera una Orden de Pedido a partir de una Cotización existente,
    copiando todos los detalles (productos, cantidades, precios)."""
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    
    # Crear la Orden de Pedido
    pedido = OrdenPedido.objects.create(
        numero=f"OP-{datetime.date.today().year}-{random.randint(1000, 9999)}",
        fecha=datetime.date.today(),
        cliente=cotizacion.cliente,
        cotizacion_referencia=cotizacion,
        subtotal=cotizacion.subtotal,
        igv=cotizacion.igv,
        total=cotizacion.total,
        estado='PENDIENTE',
    )
    
    # Copiar todos los detalles de la cotización al pedido
    for detalle in cotizacion.detalles.all():
        OrdenPedidoDetalle.objects.create(
            orden=pedido,
            producto=detalle.producto,
            presentacion=detalle.presentacion,
            cantidad=detalle.cantidad,
            precio_unitario=detalle.precio_unitario,
            subtotal=detalle.subtotal,
        )
    
    # Integración automática con Kardex
    almacen_default = Almacen.objects.first()
    if almacen_default:
        for detalle in pedido.detalles.all():
            multiplier = detalle.presentacion.cantidad_por_paquete if detalle.presentacion else 1
            cantidad_fisica = Decimal(str(detalle.cantidad)) * Decimal(str(multiplier))
            
            stock, _ = Stock.objects.get_or_create(producto=detalle.producto, almacen=almacen_default)
            stock.cantidad = Decimal(str(stock.cantidad)) - cantidad_fisica
            stock.save()
            Kardex.objects.create(
                producto=detalle.producto,
                almacen=almacen_default,
                tipo_movimiento='SALIDA',
                cantidad=cantidad_fisica,
                saldo_actual=stock.cantidad,
                motivo='Venta (Generado desde Cotización)',
                referencia=pedido.numero,
            )
    
    # Marcar cotización como Aceptada
    cotizacion.estado = 'ACEPTADA'
    cotizacion.save()
    
    messages.success(request, f"Orden de Pedido {pedido.numero} generada exitosamente desde la Cotización {cotizacion.numero}. Stock actualizado.")
    return redirect('ventas:pedido_print', pk=pedido.pk)

# ORDEN DE PEDIDO
class OrdenPedidoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = OrdenPedido
    template_name = 'ventas/pedido_list.html'
    context_object_name = 'pedidos'
    permission_required = 'ventas.view_ordenpedido'

class OrdenPedidoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = OrdenPedido
    form_class = OrdenPedidoForm
    template_name = 'ventas/pedido_form.html'
    success_url = reverse_lazy('ventas:pedido_list')
    permission_required = 'ventas.add_ordenpedido'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['detalles'] = OrdenPedidoDetalleFormSet(self.request.POST)
        else:
            data['detalles'] = OrdenPedidoDetalleFormSet()
            
        productos = Producto.objects.all()
        prices = {str(p.id): float(p.precio_venta) for p in productos}
        data['product_prices'] = json.dumps(prices)
            
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        
        form.instance.numero = f"OP-{datetime.date.today().year}-{random.randint(1000, 9999)}"
        
        if detalles.is_valid():
            self.object = form.save()
            detalles.instance = self.object
            instances = detalles.save(commit=False)
            subtotal_total = 0
            for instance in instances:
                instance.subtotal = instance.cantidad * instance.precio_unitario
                instance.save()
                subtotal_total += instance.subtotal
            
            self.object.subtotal = subtotal_total
            self.object.igv = float(subtotal_total) * 0.18
            self.object.total = float(subtotal_total) * 1.18
            self.object.save()
            
            # Integración automática con Kardex
            almacen_default = Almacen.objects.first()
            if almacen_default:
                for instance in instances:
                    # Actualizar stock considerando el multiplicador de la presentación
                    multiplier = instance.presentacion.cantidad_por_paquete if instance.presentacion else 1
                    cantidad_fisica = Decimal(str(instance.cantidad)) * Decimal(str(multiplier))
                    
                    stock, _ = Stock.objects.get_or_create(producto=instance.producto, almacen=almacen_default)
                    stock.cantidad = Decimal(str(stock.cantidad)) - cantidad_fisica
                    stock.save()

                    # Guardar movimiento en Kardex
                    Kardex.objects.create(
                        producto=instance.producto,
                        almacen=almacen_default,
                        tipo_movimiento='SALIDA',
                        cantidad=cantidad_fisica,
                        saldo_actual=stock.cantidad,
                        motivo='Venta (Orden de Pedido)',
                        referencia=self.object.numero
                    )
            
            messages.success(self.request, "Orden de Pedido creada exitosamente. Stock actualizado.")
            return redirect('ventas:pedido_print', pk=self.object.pk)
        else:
            return self.form_invalid(form)

class OrdenPedidoPrintView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = OrdenPedido
    template_name = 'ventas/pedido_print.html'
    context_object_name = 'pedido'
    permission_required = 'ventas.view_ordenpedido'

class OrdenPedidoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = OrdenPedido
    form_class = OrdenPedidoForm
    template_name = 'ventas/pedido_form.html'
    success_url = reverse_lazy('ventas:pedido_list')
    permission_required = 'ventas.change_ordenpedido'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['detalles'] = OrdenPedidoDetalleFormSet(self.request.POST, instance=self.object)
        else:
            data['detalles'] = OrdenPedidoDetalleFormSet(instance=self.object)
            
        productos = Producto.objects.all()
        prices = {str(p.id): float(p.precio_venta) for p in productos}
        data['product_prices'] = json.dumps(prices)
            
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        
        if detalles.is_valid():
            self.object = form.save()
            detalles.instance = self.object
            instances = detalles.save(commit=False)
            
            # Remove deleted models
            for obj in detalles.deleted_objects:
                obj.delete()
                
            subtotal_total = 0
            for instance in instances:
                instance.subtotal = instance.cantidad * instance.precio_unitario
                instance.save()
            
            for obj in self.object.detalles.all():
                subtotal_total += obj.subtotal
            
            self.object.subtotal = subtotal_total
            self.object.igv = float(subtotal_total) * 0.18
            self.object.total = float(subtotal_total) * 1.18
            self.object.save()
            
            messages.success(self.request, "Orden de Pedido actualizada exitosamente.")
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class OrdenPedidoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = OrdenPedido
    template_name = 'ventas/pedido_confirm_delete.html'
    success_url = reverse_lazy('ventas:pedido_list')
    permission_required = 'ventas.delete_ordenpedido'
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Orden de Pedido eliminada físicamente del sistema.")
        return super().delete(request, *args, **kwargs)

@login_required
@permission_required('ventas.change_ordenpedido', raise_exception=True)
@require_POST
def pedido_anular(request, pk):
    pedido = get_object_or_404(OrdenPedido, pk=pk)
    pedido.estado = 'ANULADA'
    pedido.save()
    messages.success(request, f"La Orden de Pedido {pedido.numero} ha sido CANCELADA.")
    return redirect('ventas:pedido_list')
