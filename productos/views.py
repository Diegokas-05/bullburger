# productos/views.py
from decimal import Decimal
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse, NoReverseMatch

# Modelos propios
from .models import Producto, Categoria, CarritoItem
from .forms import ProductoForm

# Inventario / Recetas / Movimientos
from inventario.models import Ingrediente, Receta, MovimientoInventario

# Pedido y detalle
from pedidos.models import Pedido, DetallePedido

# Usuario
from usuarios.models import Usuario

# ✅ Generador de facturas
from inventario.utils_factura import generar_factura_pdf
from django.conf import settings

# Chequeo opcional de Inventario
_INV_PRODUCTO_OK = False
try:
    from inventario.models import Inventario
    _INV_PRODUCTO_OK = True
except Exception:
    Inventario = None


# ==============================================
# 🔹 ADMINISTRADOR — CRUD PRODUCTOS Y CATEGORÍAS
# ==============================================

@login_required
def lista_productos(request):
    """Vista para listar todos los productos"""
    productos = Producto.objects.all().select_related('categoria')
    categorias = Categoria.objects.all()
    ingredientes = Ingrediente.objects.filter(activo=True)
    return render(request, 'administrador/menu.html', {
        'productos': productos,
        'categorias': categorias,
        'ingredientes': ingredientes,
    })


@login_required
def crear_producto(request):
    if request.method == 'POST':
        try:
            # Crear el producto
            producto = Producto.objects.create(
                nombre=request.POST['nombre'],
                descripcion=request.POST['descripcion'],
                precio=float(request.POST['precio']),
                categoria_id=request.POST['categoria'],
                disponible=request.POST.get('disponible') == 'on',
                imagen=request.FILES.get('imagen')
            )

            # Receta (ingredientes)
            ingredientes_data = []
            for key in request.POST.keys():
                if key.startswith('ingredientes[') and key.endswith('][id]'):
                    index = key.split('[')[1].split(']')[0]
                    ingrediente_id = request.POST[f'ingredientes[{index}][id]']
                    cantidad = request.POST.get(f'ingredientes[{index}][cantidad]')
                    
                    if ingrediente_id and cantidad:
                        ingredientes_data.append({
                            'ingrediente_id': ingrediente_id,
                            'cantidad': cantidad
                        })

            for ing in ingredientes_data:
                Receta.objects.create(
                    producto=producto,
                    ingrediente_id=ing['ingrediente_id'],
                    cantidad=ing['cantidad']
                )

            messages.success(request, 'Producto creado exitosamente con su receta')
            return redirect('menu_administrador')  # ✅ CAMBIADO
            
        except Exception as e:
            messages.error(request, f'Error al crear producto: {e}')
    return redirect('menu_administrador')


@login_required
def editar_producto(request, producto_id):
    """Vista para editar un producto existente"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('menu_administrador')
    else:
        form = ProductoForm(instance=producto)

    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    ingredientes = Ingrediente.objects.filter(activo=True)
    
    # Obtener la receta actual del producto
    recetas_actuales = Receta.objects.filter(producto=producto)

    return render(request, 'administrador/menu.html', {
        'form': form,
        'producto_editar': producto,
        'productos': productos,
        'categorias': categorias,
        'ingredientes': ingredientes,
        'recetas_actuales': recetas_actuales,
    })


@login_required
def eliminar_producto(request, producto_id):
    """Vista para eliminar un producto"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        # También eliminar las recetas asociadas
        Receta.objects.filter(producto=producto).delete()
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente')
        return redirect('menu_administrador')  # ✅ CAMBIADO
    
    return redirect('menu_administrador')  # ✅ CAMBIADO

@login_required
def crear_categoria(request):
    """Vista para crear una nueva categoría"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            messages.error(request, 'El nombre de la categoría es requerido')
        elif Categoria.objects.filter(nombre__iexact=nombre).exists():
            messages.error(request, 'Ya existe una categoría con ese nombre')
        else:
            Categoria.objects.create(nombre=nombre)
            messages.success(request, 'Categoría creada exitosamente')
    return redirect('menu_administrador')


@login_required
def eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    if request.method == 'POST':
        if Producto.objects.filter(categoria=categoria).exists():
            messages.error(request, 'No se puede eliminar una categoría con productos asociados')
        else:
            categoria.delete()
            messages.success(request, 'Categoría eliminada exitosamente')
    return redirect('menu_administrador')


# ==============================================
# 🔹 CLIENTE — MENÚ Y CARRITO
# ==============================================

def menu_cliente(request):
    categorias = Categoria.objects.all().order_by('nombre')
    productos = Producto.objects.filter(disponible=True).select_related('categoria')
    return render(request, 'cliente/menu_cliente.html', {
        'categorias': categorias,
        'productos': productos
    })


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_POST
def agregar_al_carrito(request):
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'error': 'Debe iniciar sesión para agregar productos.'}, status=403)

    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        cantidad = int(data.get('cantidad', 1))
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'ok': False, 'error': 'Datos inválidos'}, status=400)

    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Producto no encontrado'}, status=404)

    item, creado = CarritoItem.objects.get_or_create(usuario=request.user, producto=producto)
    item.cantidad = item.cantidad + cantidad if not creado else cantidad
    item.save()

    return JsonResponse({'ok': True, 'mensaje': 'Producto añadido al carrito correctamente'})


@login_required
def ver_carrito(request):
    items = CarritoItem.objects.filter(usuario=request.user).select_related('producto')
    total = sum(item.subtotal() for item in items)
    return render(request, 'cliente/carrito_cliente.html', {
        'pedidos': items,
        'total': total
    })


@login_required
@require_POST
def editar_cantidad(request, item_id):
    try:
        data = json.loads(request.body)
        nueva_cantidad = int(data.get("cantidad", 1))
        if nueva_cantidad < 1:
            return JsonResponse({"ok": False, "error": "Cantidad no válida"}, status=400)
        item = CarritoItem.objects.get(id=item_id, usuario=request.user)
        item.cantidad = nueva_cantidad
        item.save()
        return JsonResponse({"ok": True, "mensaje": "Cantidad actualizada correctamente"})
    except CarritoItem.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Item no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


@login_required
@require_POST
def eliminar_item_carrito(request, item_id):
    try:
        item = CarritoItem.objects.get(id=item_id, usuario=request.user)
        item.delete()
        return JsonResponse({"ok": True, "mensaje": "Producto eliminado del carrito"})
    except CarritoItem.DoesNotExist:
        return JsonResponse({"ok": False, "error": "El producto no existe en el carrito"}, status=404)
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


# ==============================================
# 🔹 CHECKOUT — PAGO Y GENERACIÓN DE FACTURA
# ==============================================

@login_required
@require_POST
def carrito_checkout(request):
    """Crea Pedido + Detalles + Factura PDF"""
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)

    nombre = payload.get('nombre', '').strip()
    telefono = payload.get('telefono', '').strip()
    metodo = payload.get('metodo', '').strip()
    entrega = payload.get('entrega', '').strip()
    direccion = payload.get('direccion', '').strip()
    numero_pago = payload.get('numero_pago', '').strip()

    if metodo not in ('efectivo', 'tarjeta') or entrega not in ('local', 'domicilio'):
        return JsonResponse({'ok': False, 'error': 'Datos incompletos o inválidos'}, status=400)

    if entrega == 'domicilio' and not direccion:
        return JsonResponse({'ok': False, 'error': 'La dirección es obligatoria para domicilio'}, status=400)

    if metodo == 'tarjeta' and (not numero_pago.isdigit() or not (12 <= len(numero_pago) <= 19)):
        return JsonResponse({'ok': False, 'error': 'Número de tarjeta inválido (12–19 dígitos)'}, status=400)

    items = CarritoItem.objects.select_related('producto').filter(usuario=request.user)
    if not items.exists():
        return JsonResponse({'ok': False, 'error': 'Tu bolsa está vacía'}, status=400)

    subtotal = sum((it.producto.precio * it.cantidad for it in items), Decimal('0.00'))
    total = subtotal

    try:
        with transaction.atomic():
            pedido = Pedido.objects.create(
                usuario=request.user,
                promocion=None,
                descuento_aplicado=Decimal('0.00'),
                estado='pendiente',
                tipo_entrega=entrega,
                metodo_pago=metodo,
                direccion_entrega=direccion if entrega == 'domicilio' else '',
                total=total
            )

            for it in items:
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=it.producto,
                    cantidad=it.cantidad,
                    subtotal=it.producto.precio * it.cantidad
                )

            # Inventario: productos terminados
            if _INV_PRODUCTO_OK:
                for it in items.select_for_update():
                    try:
                        inv = Inventario.objects.select_for_update().get(producto=it.producto)
                        anterior = int(inv.stock)
                        nuevo = max(0, anterior - int(it.cantidad))
                        inv.stock = nuevo
                        inv.save(update_fields=['stock'])
                        MovimientoInventario.objects.create(
                            producto=it.producto,
                            ingrediente=None,
                            tipo='salida',
                            cantidad=Decimal(it.cantidad),
                            cantidad_anterior=Decimal(anterior),
                            cantidad_nueva=Decimal(nuevo),
                            motivo=f'Venta - Pedido {pedido.id}',
                            usuario=request.user
                        )
                    except Inventario.DoesNotExist:
                        pass

            # Ingredientes según receta
            for it in items:
                recetas = Receta.objects.select_related('ingrediente').filter(producto=it.producto)
                for rec in recetas.select_for_update():
                    ing = rec.ingrediente
                    requerido = Decimal(rec.cantidad) * Decimal(it.cantidad)
                    anterior = Decimal(ing.stock_actual)
                    if anterior < requerido:
                        raise ValueError(f'Sin stock suficiente del ingrediente "{ing.nombre}"')
                    ing.stock_actual = anterior - requerido
                    ing.save(update_fields=['stock_actual'])
                    MovimientoInventario.objects.create(
                        ingrediente=ing,
                        tipo='salida',
                        cantidad=requerido,
                        cantidad_anterior=anterior,
                        cantidad_nueva=ing.stock_actual,
                        motivo=f'Consumo por venta de "{it.producto.nombre}" (Pedido {pedido.id})',
                        usuario=request.user
                    )

            # Vaciar carrito
            items.delete()

            # ✅ Generar factura PDF
            factura_url = generar_factura_pdf(pedido)
            
            factura_path_relativo = None
            if factura_url and factura_url.startswith(settings.MEDIA_URL):
                factura_path_relativo = factura_url[len(settings.MEDIA_URL):]
                if factura_path_relativo:
                    pedido.factura_pdf = factura_path_relativo
                    pedido.save(update_fields=['factura_pdf'])
                     
        return JsonResponse({
            'ok': True,
            'pedido_id': pedido.id,
            'total': f'{total:.2f}',
            'factura_url': factura_url
        })

    except ValueError as ve:
        return JsonResponse({'ok': False, 'error': str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': f'Error interno: {e}'}, status=500)
