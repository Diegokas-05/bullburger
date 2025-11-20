import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods, require_POST
from django.db import transaction
from django.db.models import Q, Sum, F, Value, DecimalField, Case, When # 👈 IMPORTACIONES DE BD
from django.db.models.functions import Coalesce # 👈 IMPORTACIÓN IMPORTANTE
from .forms import CambiarPasswordForm, UsuarioAdminForm 

from .forms import RegistroClienteForm, CustomAuthenticationForm
from .models import Usuario
from .models import Rol
from .forms import PerfilForm
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.http import FileResponse
import os
from django.utils import timezone
from datetime import datetime, date

# --- 🚀 IMPORTAR MODELOS DE OTRAS APPS ---
from productos.models import Categoria, Producto
from pedidos.models import Pedido
from inventario.models import Ingrediente
# ------------------------------------------


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

# ==============================================
# ⬇️ FUNCIÓN 'admin_dashboard' ACTUALIZADA ⬇️
# ==============================================
@login_required
def admin_dashboard(request):
    """Dashboard personalizado para administradores CON ESTADÍSTICAS"""

    # ⛔ Si NO es administrador, lo sacamos
    if not request.user.es_administrador():
        messages.error(request, "No tienes permiso para acceder al panel de administrador.")
        return redireccionar_por_rol(request.user)

    # --- Consultas de Inventario ---
    ingredientes_activos = Ingrediente.objects.filter(activo=True)
    total_ingredientes = ingredientes_activos.count()
    
    stock_bajo = ingredientes_activos.filter(
        stock_actual__lte=F('stock_minimo'),
        stock_actual__gt=0
    ).count()

    stock_agotado = ingredientes_activos.filter(
        stock_actual__lte=0
    ).count()

    valor_inventario_query = ingredientes_activos.annotate(
        costo_unit=Case(
            When(tamaño_paquete__gt=0, then=F('precio_paquete') / F('tamaño_paquete')),
            default=Value(0),
            output_field=DecimalField()
        )
    ).annotate(
        valor_item=F('stock_actual') * F('costo_unit')
    ).aggregate(
        valor_total=Coalesce(Sum('valor_item'), Value(0, output_field=DecimalField()))
    )
    valor_total_inventario = valor_inventario_query['valor_total']

    # --- Productos ---
    total_productos = Producto.objects.count()
    total_categorias = Categoria.objects.count()

    # --- Pedidos ---
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    pedidos_preparando = Pedido.objects.filter(estado='preparando').count()
    
    ventas_totales_query = Pedido.objects.filter(estado='entregado').aggregate(
        total_ventas=Coalesce(Sum('total'), Value(0, output_field=DecimalField()))
    )
    ventas_totales = ventas_totales_query['total_ventas']

    context = {
        'total_ingredientes': total_ingredientes,
        'total_stock_bajo': stock_bajo,
        'total_stock_agotado': stock_agotado,
        'valor_total_inventario': valor_total_inventario,
        'total_productos': total_productos,
        'total_categorias': total_categorias,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_preparando': pedidos_preparando,
        'ventas_totales': ventas_totales,
    }
    
    return render(request, 'administrador/dashboard.html', context)

# ==============================================
# ⬆️ FIN DE LA FUNCIÓN ACTUALIZADA ⬆️
# ==============================================


@login_required
def empleado_dashboard(request):
    if not request.user.es_empleado():
        messages.error(request, "No tienes permiso para acceder al panel de empleado.")
        return redireccionar_por_rol(request.user)

    return render(request, 'empleado/dashboard.html')

@login_required
def cliente_dashboard(request):
    if not request.user.es_cliente():
        messages.error(request, "No tienes permiso para acceder al panel de cliente.")
        return redireccionar_por_rol(request.user)

    return render(request, 'cliente/dashboard.html')

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
    
    # Redirigir a la página desde donde se llamó (probablemente 'menu_administrador')
    return redirect(request.POST.get('next', 'admin_dashboard'))


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
@require_POST
def crear_cliente(request):
    """
    Crea un usuario con rol 'Cliente' desde el modal de lista_clientes.
    Recibe JSON: nombre, email, telefono, direccion, password, password2.
    Devuelve: {ok: True, id} o {ok: False, errors}.
    """
    
    data = json.loads(request.body or '{}')

    # Rol "Cliente"
    rol_cliente, _ = Rol.objects.get_or_create(nombre='Cliente')
    data.setdefault('rol', rol_cliente.id)
    data.setdefault('is_active', True)

    
    form = UsuarioAdminForm(data=data)
    if form.is_valid():
        user = form.save()
        return JsonResponse({'ok': True, 'id': user.id})

    
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

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
        
        # Mantener el rol de empleado
        rol_empleado, _ = Rol.objects.get_or_create(nombre='Empleado')
        data.setdefault('rol', rol_empleado.id)
        data.setdefault('is_active', empleado.is_active)

        form = UsuarioAdminForm(data=data, instance=empleado)
        if form.is_valid():
            nombre_anterior = empleado.nombre
            user = form.save()
            # ✅ AGREGAR MENSAJE DE ÉXITO
            messages.success(request, f'Empleado "{nombre_anterior}" modificado correctamente')
            return JsonResponse({'ok': True})
        
        # ✅ AGREGAR MENSAJE DE ERROR
        error_msg = '; '.join([f"{k}: {', '.join(v)}" for k, v in form.errors.items()])
        messages.error(request, f'Error al actualizar empleado: {error_msg}')
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


@login_required
@require_POST
def eliminar_empleado(request, id):
    empleado = get_object_or_404(Usuario, id=id)
    nombre_empleado = empleado.nombre
    
    try:
        empleado.delete()
        # ✅ AGREGAR MENSAJE DE ÉXITO
        messages.success(request, f'Empleado "{nombre_empleado}" eliminado exitosamente')
        return JsonResponse({'ok': True})
    except Exception as e:
        # ✅ AGREGAR MENSAJE DE ERROR
        messages.error(request, f'Error al eliminar empleado: {str(e)}')
        return JsonResponse({'ok': False, 'msg': f'Error al eliminar empleado: {str(e)}'})


@login_required
def crear_empleado(request):
    if request.method == "GET":
        return JsonResponse({'ok': True, 'data': {}})

    data = json.loads(request.body or '{}')

    rol_empleado, _ = Rol.objects.get_or_create(nombre='Empleado')
    data.setdefault('rol', rol_empleado.id)
    data.setdefault('is_active', True)

    form = UsuarioAdminForm(data=data)
    if form.is_valid():
        user = form.save()
        # ✅ AGREGAR MENSAJE DE ÉXITO
        messages.success(request, f'Empleado "{user.nombre}" creado exitosamente')
        return JsonResponse({'ok': True, 'id': user.id})
    
    # ✅ AGREGAR MENSAJE DE ERROR
    error_msg = '; '.join([f"{k}: {', '.join(v)}" for k, v in form.errors.items()])
    messages.error(request, f'Error al crear empleado: {error_msg}')
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

@login_required
def perfil_usuario(request):
    return render(request, 'usuarios/perfil.html', {})

@login_required
@require_POST
def perfil_actualizar(request):
    data = json.loads(request.body or '{}')
    data.setdefault('email', request.user.email)
    form = PerfilForm(data, instance=request.user)
    if form.is_valid():
        form.save()
        return JsonResponse({'ok': True})
    err = '; '.join([f"{k}: {', '.join(v)}" for k, v in form.errors.items()])
    return JsonResponse({'ok': False, 'msg': err}, status=400)

@login_required
@require_POST
def perfil_cambiar_password(request):
    if request.headers.get('Content-Type', '').startswith('application/json'):
        data = json.loads(request.body or '{}')
    else:
        data = request.POST

    form = CambiarPasswordForm(user=request.user, data=data)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return JsonResponse({'ok': True})

    errores = {k: v for k, v in form.errors.items()}
    return JsonResponse({'ok': False, 'errors': errores, 'msg': '; '.join(
        f"{k}: {', '.join(v)}" for k, v in errores.items()
    )}, status=400)
    

@login_required
def pedidos_cliente_view(request):
    pedidos_list = Pedido.objects.filter(
        usuario=request.user
    ).prefetch_related(
        'detallepedido_set__producto'
    ).order_by('-fecha')

    context = {
        'pedidos': pedidos_list
    }
    return render(request, 'cliente/pedidos_cliente.html', context)

@login_required
def descargar_factura(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    f = pedido.factura_pdf
    if not (f and f.name and default_storage.exists(f.name)):
        messages.warning(request, "La factura no está disponible.")
        return redirect("pedidos_cliente")
    return FileResponse(f.open("rb"), as_attachment=True, filename=os.path.basename(f.name))



#metods para empleados
@login_required
def gestion_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-fecha')
    
    pedidos_pendientes = pedidos.filter(estado='pendiente')
    pedidos_preparando = pedidos.filter(estado='preparando')
    pedidos_listos = pedidos.filter(estado='listo')
    pedidos_entregados = pedidos.filter(estado='entregado')
    
    context = {
        'pedidos': pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_preparando': pedidos_preparando,
        'pedidos_listos': pedidos_listos,
        'pedidos_entregados': pedidos_entregados,
    }
    return render(request, 'empleado/gestion_pedidos.html', context)

@csrf_exempt
@login_required
def actualizar_estado_pedido(request, pedido_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nuevo_estado = data.get('nuevo_estado')
            
            pedido = get_object_or_404(Pedido, id=pedido_id)
            pedido.estado = nuevo_estado
            pedido.save()
            
            return JsonResponse({'success': True, 'nuevo_estado': nuevo_estado})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def dashboard_empleado(request):
    """Vista del dashboard para empleados con estadísticas"""
    try:
        hoy = date.today()
        
        pedidos_hoy = Pedido.objects.filter(fecha__date=hoy)
        
        # Estadísticas
        total_pedidos = pedidos_hoy.count()
        pedidos_pendientes_count = pedidos_hoy.filter(estado='pendiente').count()
        pedidos_preparando_count = pedidos_hoy.filter(estado='preparando').count()
        pedidos_listos_count = pedidos_hoy.filter(estado='listo').count()
        
        context = {
            'total_pedidos': total_pedidos,
            'pedidos_pendientes': pedidos_hoy.filter(estado='pendiente'),
            'pedidos_preparando': pedidos_hoy.filter(estado='preparando'),
            'pedidos_listos': pedidos_hoy.filter(estado='listo'),
            'now': timezone.now(),
        }
        return render(request, 'empleado/dashboard.html', context)
        
    except Exception as e:
        print(f"ERROR en dashboard: {e}")
        # Vista de fallback
        context = {
            'total_pedidos': 0,
            'pedidos_pendientes': [],
            'pedidos_preparando': [],
            'pedidos_listos': [],
            'now': timezone.now(),
        }
        return render(request, 'empleado/dashboard.html', context)

@login_required
def api_estadisticas(request):
    """API para obtener estadísticas en tiempo real"""
    try:
        hoy = date.today()
        pedidos_hoy = Pedido.objects.filter(fecha__date=hoy)
        
        data = {
            'total_pedidos': pedidos_hoy.count(),
            'pedidos_pendientes': pedidos_hoy.filter(estado='pendiente').count(),
            'pedidos_preparando': pedidos_hoy.filter(estado='preparando').count(),
            'pedidos_listos': pedidos_hoy.filter(estado='listo').count(),
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        print(f"ERROR en api_estadisticas: {e}")
        return JsonResponse({
            'total_pedidos': 0,
            'pedidos_pendientes': 0,
            'pedidos_preparando': 0,
            'pedidos_listos': 0,
        })