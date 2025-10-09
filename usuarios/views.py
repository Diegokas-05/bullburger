from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroClienteForm, CustomAuthenticationForm
from .models import Usuario

def redireccionar_por_rol(user):
    if user.es_administrador():
        return redirect('admin_dashboard')
    elif user.es_empleado():
        return redirect('empleado_dashboard')
    elif user.es_cliente():
        return redirect('cliente_dashboard')
    else:
        return redirect('login')

def login_view(request):
    if request.user.is_authenticated:
        return redireccionar_por_rol(request.user)
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.nombre}!')
                return redireccionar_por_rol(user)
        messages.error(request, 'Email o contraseña incorrectos')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'usuarios/login.html', {'form': form})

def registro_cliente_view(request):
    if request.user.is_authenticated:
        return redireccionar_por_rol(request.user)
    
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Cuenta creada exitosamente! Bienvenido {user.nombre}')
            return redirect('cliente_dashboard')
        else:
            # Mostrar errores específicos del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    else:
        form = RegistroClienteForm()
    
    return render(request, 'usuarios/registro_cliente.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, '¡Sesión cerrada exitosamente!')
    return redirect('login')

@login_required
def admin_dashboard(request):
    """Dashboard personalizado para administradores"""
    return render(request, 'administrador/dashboard.html')  # ← CAMBIADO: 'administrador/'

@login_required
def empleado_dashboard(request):
    return render(request, 'empleado/dashboard.html')

@login_required
def cliente_dashboard(request):
    return render(request, 'cliente/dashboard.html')


def administrador_menu(request):
    return render (request,'administrador/menu.html')