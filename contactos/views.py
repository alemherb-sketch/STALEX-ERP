from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from .models import Cliente, Proveedor, Transportista
from .forms import ClienteForm, ProveedorForm, TransportistaForm

# CLIENTES
class ClienteListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Cliente
    template_name = 'contactos/cliente_list.html'
    context_object_name = 'clientes'
    permission_required = 'contactos.view_cliente'

class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'contactos/cliente_form.html'
    success_url = reverse_lazy('contactos:cliente_list')
    success_message = "Cliente creado exitosamente."
    permission_required = 'contactos.add_cliente'

class ClienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'contactos/cliente_form.html'
    success_url = reverse_lazy('contactos:cliente_list')
    success_message = "Cliente actualizado exitosamente."
    permission_required = 'contactos.change_cliente'

class ClienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'contactos/cliente_confirm_delete.html'
    success_url = reverse_lazy('contactos:cliente_list')
    permission_required = 'contactos.delete_cliente'

# PROVEEDORES
class ProveedorListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Proveedor
    template_name = 'contactos/proveedor_list.html'
    context_object_name = 'proveedores'
    permission_required = 'contactos.view_proveedor'

class ProveedorCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'contactos/proveedor_form.html'
    success_url = reverse_lazy('contactos:proveedor_list')
    success_message = "Proveedor creado exitosamente."
    permission_required = 'contactos.add_proveedor'

class ProveedorUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'contactos/proveedor_form.html'
    success_url = reverse_lazy('contactos:proveedor_list')
    success_message = "Proveedor actualizado exitosamente."
    permission_required = 'contactos.change_proveedor'

class ProveedorDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Proveedor
    template_name = 'contactos/proveedor_confirm_delete.html'
    success_url = reverse_lazy('contactos:proveedor_list')
    permission_required = 'contactos.delete_proveedor'

# TRANSPORTISTAS
class TransportistaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Transportista
    template_name = 'contactos/transportista_list.html'
    context_object_name = 'transportistas'
    permission_required = 'contactos.view_transportista'

class TransportistaCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Transportista
    form_class = TransportistaForm
    template_name = 'contactos/transportista_form.html'
    success_url = reverse_lazy('contactos:transportista_list')
    success_message = "Transportista creado exitosamente."
    permission_required = 'contactos.add_transportista'

class TransportistaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Transportista
    form_class = TransportistaForm
    template_name = 'contactos/transportista_form.html'
    success_url = reverse_lazy('contactos:transportista_list')
    success_message = "Transportista actualizado exitosamente."
    permission_required = 'contactos.change_transportista'

class TransportistaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Transportista
    template_name = 'contactos/transportista_confirm_delete.html'
    success_url = reverse_lazy('contactos:transportista_list')
    permission_required = 'contactos.delete_transportista'
