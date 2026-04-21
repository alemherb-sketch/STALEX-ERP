from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import OrdenDespacho, OrdenDespachoDetalle
from .forms import OrdenDespachoForm, OrdenDespachoDetalleFormSet
from ventas.models import OrdenPedido
from decimal import Decimal
import random
import datetime

class OrdenDespachoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = OrdenDespacho
    template_name = 'logistica/despacho_list.html'
    context_object_name = 'despachos'
    permission_required = 'logistica.view_ordendespacho'

class OrdenDespachoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = OrdenDespacho
    form_class = OrdenDespachoForm
    template_name = 'logistica/despacho_form.html'
    success_url = reverse_lazy('logistica:despacho_list')
    permission_required = 'logistica.add_ordendespacho'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['detalles'] = OrdenDespachoDetalleFormSet(self.request.POST)
        else:
            data['detalles'] = OrdenDespachoDetalleFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        
        form.instance.numero = f"GUI-{datetime.date.today().year}-{random.randint(1000, 9999)}"
        
        if detalles.is_valid():
            self.object = form.save()
            detalles.instance = self.object
            detalles.save()
            messages.success(self.request, "Orden de Despacho creada exitosamente.")
            return redirect('logistica:despacho_print', pk=self.object.pk)
        else:
            return self.form_invalid(form)

class OrdenDespachoPrintView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = OrdenDespacho
    template_name = 'logistica/despacho_print.html'
    context_object_name = 'despacho'
    permission_required = 'logistica.view_ordendespacho'

class OrdenDespachoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = OrdenDespacho
    form_class = OrdenDespachoForm
    template_name = 'logistica/despacho_form.html'
    success_url = reverse_lazy('logistica:despacho_list')
    permission_required = 'logistica.change_ordendespacho'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['detalles'] = OrdenDespachoDetalleFormSet(self.request.POST, instance=self.object)
        else:
            data['detalles'] = OrdenDespachoDetalleFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        
        if detalles.is_valid():
            self.object = form.save()
            detalles.instance = self.object
            detalles.save()
            
            messages.success(self.request, "Orden de Despacho actualizada exitosamente.")
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class OrdenDespachoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = OrdenDespacho
    template_name = 'logistica/despacho_confirm_delete.html'
    success_url = reverse_lazy('logistica:despacho_list')
    permission_required = 'logistica.delete_ordendespacho'
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Orden de Despacho eliminada del sistema.")
        return super().delete(request, *args, **kwargs)

@login_required
@permission_required('logistica.change_ordendespacho', raise_exception=True)
@require_POST
def despacho_anular(request, pk):
    despacho = get_object_or_404(OrdenDespacho, pk=pk)
    despacho.estado = 'ANULADO'
    despacho.save()
    messages.success(request, f"El Despacho {despacho.numero} ha sido ANULADO.")
    return redirect('logistica:despacho_list')


@login_required
@permission_required('logistica.add_ordendespacho', raise_exception=True)
@require_POST
def generar_despacho_consolidado(request):
    """Genera una Orden de Despacho consolidada a partir de múltiples Órdenes de Pedido."""
    pedido_ids = request.POST.getlist('pedidos_seleccionados')
    
    if not pedido_ids:
        messages.error(request, "Debe seleccionar al menos una Orden de Pedido.")
        return redirect('ventas:pedido_list')
    
    pedidos = OrdenPedido.objects.filter(pk__in=pedido_ids)
    
    if not pedidos.exists():
        messages.error(request, "No se encontraron las órdenes seleccionadas.")
        return redirect('ventas:pedido_list')
    
    # Crear la Orden de Despacho
    despacho = OrdenDespacho.objects.create(
        numero=f"GUI-{datetime.date.today().year}-{random.randint(1000, 9999)}",
        fecha=datetime.date.today(),
        direccion_origen="Almacén Principal - Av. Industrial 123, Lima",
        direccion_destino=pedidos.first().cliente.direccion or "Por definir",
        peso_total=Decimal('0.00'),
        estado='PROGRAMADO',
    )
    
    # Asociar las órdenes de pedido
    despacho.ordenes_pedido.set(pedidos)
    
    # Consolidar productos: agrupar por producto y sumar cantidades
    productos_consolidados = {}
    for pedido in pedidos:
        for detalle in pedido.detalles.all():
            prod_id = detalle.producto.pk
            if prod_id in productos_consolidados:
                productos_consolidados[prod_id]['cantidad'] += detalle.cantidad
            else:
                productos_consolidados[prod_id] = {
                    'producto': detalle.producto,
                    'cantidad': detalle.cantidad,
                }
    
    # Crear los detalles consolidados y calcular peso total
    peso_total = Decimal('0.00')
    for prod_id, data in productos_consolidados.items():
        OrdenDespachoDetalle.objects.create(
            despacho=despacho,
            producto=data['producto'],
            cantidad=data['cantidad'],
        )
        peso_total += data['cantidad'] * data['producto'].peso
    
    despacho.peso_total = peso_total
    despacho.save()
    
    # Marcar los pedidos como despachados
    pedidos.update(estado='DESPACHADA')
    
    numeros = ', '.join(p.numero for p in pedidos)
    messages.success(request, f"Despacho {despacho.numero} generado consolidando: {numeros}. Peso total: {peso_total} Kg.")
    return redirect('logistica:despacho_print', pk=despacho.pk)

@login_required
@permission_required('logistica.add_ordendespacho', raise_exception=True)
@require_POST
def generar_despacho_individual(request, pk):
    """Genera una Orden de Despacho directamente para una única Orden de Pedido."""
    pedido = get_object_or_404(OrdenPedido, pk=pk)
    
    if pedido.estado == 'DESPACHADA':
        messages.warning(request, f"La Orden de Pedido {pedido.numero} ya ha sido despachada anteriormente.")
        return redirect('ventas:pedido_list')
    
    if pedido.estado == 'ANULADA':
        messages.error(request, f"No se puede despachar una Orden de Pedido que ha sido ANULADA.")
        return redirect('ventas:pedido_list')

    # Crear la Orden de Despacho
    despacho = OrdenDespacho.objects.create(
        numero=f"GUI-{datetime.date.today().year}-{random.randint(1000, 9999)}",
        fecha=datetime.date.today(),
        direccion_origen="Almacén Principal - Av. Industrial 123, Lima",
        direccion_destino=pedido.cliente.direccion or "Por definir",
        peso_total=Decimal('0.00'),
        estado='PROGRAMADO',
    )
    
    # Asociar la orden de pedido
    despacho.ordenes_pedido.add(pedido)
    
    # Copiar detalles del pedido al despacho y calcular peso
    peso_total = Decimal('0.00')
    for detalle in pedido.detalles.all():
        OrdenDespachoDetalle.objects.create(
            despacho=despacho,
            producto=detalle.producto,
            cantidad=detalle.cantidad,
        )
        peso_total += detalle.cantidad * detalle.producto.peso
    
    despacho.peso_total = peso_total
    despacho.save()
    
    # Marcar el pedido como despachado
    pedido.estado = 'DESPACHADA'
    pedido.save()
    
    messages.success(request, f"Despacho {despacho.numero} generado para el pedido {pedido.numero}. Peso total: {peso_total} Kg.")
    return redirect('logistica:despacho_print', pk=despacho.pk)

class OrdenDespachoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = OrdenDespacho
    template_name = 'logistica/despacho_detail.html'
    context_object_name = 'despacho'
    permission_required = 'logistica.view_ordendespacho'

@login_required
@permission_required('logistica.change_ordendespacho', raise_exception=True)
@require_POST
def despacho_entregar(request, pk):
    """Marca una Orden de Despacho como ENTREGADO."""
    despacho = get_object_or_404(OrdenDespacho, pk=pk)
    despacho.estado = 'ENTREGADO'
    despacho.save()
    messages.success(request, f"El Despacho {despacho.numero} ha sido marcado como ENTREGADO exitosamente.")
    return redirect('logistica:despacho_detail', pk=despacho.pk)
