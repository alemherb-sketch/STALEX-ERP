from django.urls import path
from . import views

app_name = 'logistica'

urlpatterns = [
    path('despachos/', views.OrdenDespachoListView.as_view(), name='despacho_list'),
    path('despachos/nuevo/', views.OrdenDespachoCreateView.as_view(), name='despacho_create'),
    path('despachos/consolidar/', views.generar_despacho_consolidado, name='despacho_consolidar'),
    path('despachos/<int:pk>/editar/', views.OrdenDespachoUpdateView.as_view(), name='despacho_update'),
    path('despachos/<int:pk>/eliminar/', views.OrdenDespachoDeleteView.as_view(), name='despacho_delete'),
    path('despachos/<int:pk>/anular/', views.despacho_anular, name='despacho_anular'),
    path('despachos/<int:pk>/', views.OrdenDespachoDetailView.as_view(), name='despacho_detail'),
    path('despachos/<int:pk>/entregar/', views.despacho_entregar, name='despacho_entregar'),
    path('despachos/pedido/<int:pk>/generar/', views.generar_despacho_individual, name='despacho_individual'),
    path('despachos/<int:pk>/imprimir/', views.OrdenDespachoPrintView.as_view(), name='despacho_print'),
]
