from django.urls import path
from . import views

app_name = 'contactos'

urlpatterns = [
    # Clientes
    path('clientes/', views.ClienteListView.as_view(), name='cliente_list'),
    path('clientes/nuevo/', views.ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/editar/<int:pk>/', views.ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/eliminar/<int:pk>/', views.ClienteDeleteView.as_view(), name='cliente_delete'),
    
    # Proveedores
    path('proveedores/', views.ProveedorListView.as_view(), name='proveedor_list'),
    path('proveedores/nuevo/', views.ProveedorCreateView.as_view(), name='proveedor_create'),
    path('proveedores/editar/<int:pk>/', views.ProveedorUpdateView.as_view(), name='proveedor_update'),
    path('proveedores/eliminar/<int:pk>/', views.ProveedorDeleteView.as_view(), name='proveedor_delete'),
    
    # Transportistas
    path('transportistas/', views.TransportistaListView.as_view(), name='transportista_list'),
    path('transportistas/nuevo/', views.TransportistaCreateView.as_view(), name='transportista_create'),
    path('transportistas/editar/<int:pk>/', views.TransportistaUpdateView.as_view(), name='transportista_update'),
    path('transportistas/eliminar/<int:pk>/', views.TransportistaDeleteView.as_view(), name='transportista_delete'),
]
