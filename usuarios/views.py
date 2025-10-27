import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods, require_POST
from django.db import transaction
from django.db.models import Q  # Útil si usas buscadores con filtros dinámicos
from .forms import UsuarioAdminForm 

from .forms import RegistroClienteForm, CustomAuthenticationForm
from .models import Usuario
import json
from .models import Rol

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

"""@login_required
def administrador_menu(request):
    return render (request,'administrador/menu.html')"""

@login_required
def crear_categoria(request):
    """Vista para crear una nueva categoría"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            categoria, created = Categoria.objects.get_or_create(nombre=nombre)
            if created:
                messages.success(request, f'Categoría "{nombre}" creada exitosamente!')
            else:
                messages.info(request, f'La categoría "{nombre}" ya existe.')
        else:
            messages.error(request, 'El nombre de la categoría es requerido.')
    
    return redirect('lista_productos')


@login_required
def lista_clientes(request):
    """Muestra los usuarios con rol 'Cliente' y permite buscarlos."""
    clientes = Usuario.objects.filter(rol__nombre='Cliente')

    query = request.GET.get('buscar')
    if query:
        clientes = clientes.filter(
            Q(nombre__icontains=query) |
            Q(email__icontains=query)
        )

    context = {'clientes': clientes}
    return render(request, 'administrador/lista_clientes.html', context)

@login_required
def lista_administradores(request):
    
    admins = Usuario.objects.filter(rol__nombre='Administrador').order_by('-date_joined')

    query = request.GET.get('buscar', '').strip()
    if query:
        admins = admins.filter(
            Q(nombre__icontains=query) |
            Q(email__icontains=query)
        )

    context = {'admins': admins}
    return render(request, 'administrador/lista_administradores.html', context)


def crear_administrador(request):
    if request.method == "GET":
        return JsonResponse({'ok': True, 'data': {}})

    data = json.loads(request.body or '{}')


    from .models import Rol
    rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador')
    data.setdefault('rol', rol_admin.id)
    data.setdefault('is_active', True)

    form = UsuarioAdminForm(data=data)
    if form.is_valid():
        user = form.save()
        return JsonResponse({'ok': True, 'id': user.id})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)



@login_required
def editar_cliente(request, id):
    c = get_object_or_404(Usuario, id=id)

    if request.method == 'GET':
        return JsonResponse({
            'id': c.id,
            'nombre': c.nombre or '',
            'email': c.email or '',
            'telefono': c.telefono or '',
            'direccion': c.direccion or '',
        })

    if request.method == 'POST':
        data = json.loads(request.body or '{}')
        for f in ('nombre', 'email', 'telefono', 'direccion'):
            if f in data:
                setattr(c, f, (data[f] or None))
        c.save()
        return JsonResponse({'success': True})

    return HttpResponseNotAllowed(['GET', 'POST'])



@login_required
@require_http_methods(["GET", "POST"])
def editar_administrador(request, id):
    u = get_object_or_404(Usuario, id=id, rol__nombre='Administrador')

    if request.method == 'GET':
        return JsonResponse({
            'id': u.id,
            'nombre': u.nombre or '',
            'email': u.email or '',
            'telefono': u.telefono or '',
            'direccion': u.direccion or '',
        })

    data = json.loads(request.body or '{}')

    # ✅ Mantener campos críticos si no llegan del modal
    if 'rol' not in data:
        data['rol'] = u.rol_id
    if 'is_active' not in data:
        data['is_active'] = u.is_active

    form = UsuarioAdminForm(data=data, instance=u)
    if form.is_valid():
        form.save()
        return JsonResponse({'ok': True, 'msg': 'Administrador actualizado'})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)



@login_required
@require_POST
def eliminar_cliente(request, id):
    get_object_or_404(Usuario, id=id).delete()
    return JsonResponse({'success': True})


@login_required
@require_POST
def eliminar_administrador(request, id):
    u = get_object_or_404(Usuario, id=id, rol__nombre='Administrador')
    if request.user.id == u.id:
        return JsonResponse({'ok': False, 'msg': 'No puedes eliminar tu propia cuenta.'}, status=400)
    u.delete()
    return JsonResponse({'ok': True})

@login_required
def lista_empleados(request):
    """Muestra los usuarios con rol 'Empleado' y permite buscarlos."""
    empleados = Usuario.objects.filter(rol__nombre='Empleado')

    query = request.GET.get('buscar')
    if query:
        empleados = empleados.filter(
            Q(nombre__icontains=query) |
            Q(email__icontains=query)
        )

    context = {'empleados': empleados}
    return render(request, 'administrador/lista_empleados.html', context)


@login_required
def editar_empleado(request, id):
    empleado = get_object_or_404(Usuario, id=id)

    if request.method == 'GET':
        return JsonResponse({
            'id': empleado.id,
            'nombre': empleado.nombre or '',
            'email': empleado.email or '',
            'telefono': empleado.telefono or '',
            'direccion': empleado.direccion or '',
        })

    if request.method == 'POST':
        data = json.loads(request.body or '{}')
        for campo in ('nombre', 'email', 'telefono', 'direccion'):
            if campo in data:
                setattr(empleado, campo, (data[campo] or None))
        empleado.save()
        return JsonResponse({'success': True})

    return HttpResponseNotAllowed(['GET', 'POST'])


@login_required
@require_POST
def eliminar_empleado(request, id):
    get_object_or_404(Usuario, id=id).delete()
    return JsonResponse({'success': True})


def crear_empleado(request):
    if request.method == "GET":
        return JsonResponse({'ok': True, 'data': {}})

    data = json.loads(request.body or '{}')

    rol_empleado, _ = Rol.objects.get_or_create(nombre='Empleado')
    data.setdefault('rol', rol_empleado.id)
    data.setdefault('is_active', True)

    form = UsuarioAdminForm(data=data)
    if form.is_valid():
        empleado = form.save()
        return JsonResponse({'ok': True, 'id': empleado.id})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)