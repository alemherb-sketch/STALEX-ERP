from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.UsuarioListView.as_view(), name='user_list'),
    path('crear/', views.UsuarioCreateView.as_view(), name='user_create'),
    path('editar/<int:pk>/', views.UsuarioUpdateView.as_view(), name='user_update'),
]
