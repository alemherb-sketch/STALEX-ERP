from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('cotizaciones/', views.CotizacionListView.as_view(), name='cotizacion_list'),
    path('cotizaciones/nueva/', views.CotizacionCreateView.as_view(), name='cotizacion_create'),
    path('cotizaciones/<int:pk>/editar/', views.CotizacionUpdateView.as_view(), name='cotizacion_update'),
    path('cotizaciones/<int:pk>/eliminar/', views.CotizacionDeleteView.as_view(), name='cotizacion_delete'),
    path('cotizaciones/<int:pk>/anular/', views.cotizacion_anular, name='cotizacion_anular'),
    path('cotizaciones/<int:pk>/generar-pedido/', views.cotizacion_generar_pedido, name='cotizacion_generar_pedido'),
    path('cotizaciones/<int:pk>/imprimir/', views.CotizacionPrintView.as_view(), name='cotizacion_print'),
    
    path('pedidos/', views.OrdenPedidoListView.as_view(), name='pedido_list'),
    path('pedidos/nuevo/', views.OrdenPedidoCreateView.as_view(), name='pedido_create'),
    path('pedidos/<int:pk>/editar/', views.OrdenPedidoUpdateView.as_view(), name='pedido_update'),
    path('pedidos/<int:pk>/eliminar/', views.OrdenPedidoDeleteView.as_view(), name='pedido_delete'),
    path('pedidos/<int:pk>/anular/', views.pedido_anular, name='pedido_anular'),
    path('pedidos/<int:pk>/imprimir/', views.OrdenPedidoPrintView.as_view(), name='pedido_print'),
]
