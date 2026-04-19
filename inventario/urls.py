from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('productos/', views.ProductoListView.as_view(), name='producto_list'),
    path('productos/nuevo/', views.ProductoCreateView.as_view(), name='producto_create'),
    path('productos/editar/<int:pk>/', views.ProductoUpdateView.as_view(), name='producto_update'),
    path('productos/eliminar/<int:pk>/', views.ProductoDeleteView.as_view(), name='producto_delete'),
    path('productos/api/info/<int:product_id>/', views.get_product_details, name='get_product_details'),
    
    path('almacenes/', views.AlmacenListView.as_view(), name='almacen_list'),
    path('almacenes/nuevo/', views.AlmacenCreateView.as_view(), name='almacen_create'),
    path('almacenes/editar/<int:pk>/', views.AlmacenUpdateView.as_view(), name='almacen_update'),
    path('almacenes/eliminar/<int:pk>/', views.AlmacenDeleteView.as_view(), name='almacen_delete'),
    
    path('kardex/', views.KardexListView.as_view(), name='kardex_list'),
    path('stock/', views.StockSummaryView.as_view(), name='stock_list'),
    
    path('movimientos/', views.MovimientoAlmacenListView.as_view(), name='movimiento_almacen_list'),
    path('movimientos/nuevo/', views.MovimientoAlmacenCreateView.as_view(), name='movimiento_almacen_create'),
]
