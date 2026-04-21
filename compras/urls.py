from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('ordenes/', views.OrdenCompraListView.as_view(), name='orden_compra_list'),
    path('ordenes/nuevo/', views.OrdenCompraCreateView.as_view(), name='orden_compra_create'),
    path('ordenes/editar/<int:pk>/', views.OrdenCompraUpdateView.as_view(), name='orden_compra_update'),
    path('ordenes/eliminar/<int:pk>/', views.OrdenCompraDeleteView.as_view(), name='orden_compra_delete'),
    path('ordenes/imprimir/<int:pk>/', views.OrdenCompraPrintView.as_view(), name='orden_compra_print'),
    path('ordenes/recibir/<int:pk>/', views.recibir_orden_compra, name='orden_compra_recibir'),
]
