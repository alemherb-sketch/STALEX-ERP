from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib import messages

# Helper para traducir permisos al vuelo
class TranslatedPermissionMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        name = obj.name
        name = name.replace("Can add", "Puede añadir")
        name = name.replace("Can change", "Puede editar")
        name = name.replace("Can delete", "Puede eliminar")
        name = name.replace("Can view", "Puede ver")
        
        # Opcional: traducir nombres de la app si están en ingles (ej. auth)
        app_label = obj.content_type.app_label
        app_dict = {'auth': 'Autenticación', 'admin': 'Administración', 'contenttypes': 'Tipos de contenido', 'sessions': 'Sesiones'}
        app_name = app_dict.get(app_label, app_label.capitalize())
        
        return f"{app_name} | {obj.content_type.name.capitalize()} | {name}"

# Forms
class CustomUserCreationForm(UserCreationForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(), 
        widget=forms.CheckboxSelectMultiple, 
        required=False, 
        label="Roles/Grupos"
    )
    user_permissions = TranslatedPermissionMultipleChoiceField(
        queryset=Permission.objects.all(), 
        widget=forms.CheckboxSelectMultiple, 
        required=False, 
        label="Permisos Específicos"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'groups', 'user_permissions')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['first_name', 'last_name', 'email']:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class UserUpdateForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(), 
        widget=forms.CheckboxSelectMultiple, 
        required=False, 
        label="Roles/Grupos"
    )
    user_permissions = TranslatedPermissionMultipleChoiceField(
        queryset=Permission.objects.all(), 
        widget=forms.CheckboxSelectMultiple, 
        required=False, 
        label="Permisos Específicos"
    )
    new_password = forms.CharField(
        label="Nueva Contraseña", 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Dejar en blanco para no cambiar'}), 
        required=False,
        help_text="Opcional. Ingresa una nueva clave solo si deseas cambiar la actual."
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'groups', 'user_permissions']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

# Views
class UsuarioListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = 'usuarios/user_list.html'
    context_object_name = 'usuarios'
    permission_required = 'auth.view_user'

class UsuarioCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'usuarios/user_form.html'
    success_url = reverse_lazy('usuarios:user_list')
    permission_required = 'auth.add_user'
    
    def form_valid(self, form):
        messages.success(self.request, "Usuario creado correctamente.")
        return super().form_valid(form)

class UsuarioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'usuarios/user_form.html'
    success_url = reverse_lazy('usuarios:user_list')
    permission_required = 'auth.change_user'
    
    def form_valid(self, form):
        user = form.save(commit=False)
        new_password = form.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        user.save()
        form.save_m2m()
        
        messages.success(self.request, "Usuario actualizado correctamente.")
        return super().form_valid(form)
