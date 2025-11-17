# inventario/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import models
from .models import Ingrediente, Receta, MovimientoInventario, Producto
from .forms import IngredienteForm, AjusteInventarioForm

@login_required
def lista_inventario(request):
    ingredientes = Ingrediente.objects.filter(activo=True)
    
    # Esta consulta SÍ la necesitas para las alertas en la página de inventario
    ingredientes_bajos = ingredientes.filter(
        models.Q(stock_actual__lte=models.F('stock_minimo')) | 
        models.Q(stock_actual__lte=0)
    )
    
    # Eliminamos las estadísticas que se movieron al dashboard
    context = {
        'ingredientes': ingredientes,
        'ingredientes_bajos': ingredientes_bajos,
    }
    return render(request, 'inventario/inventario.html', context)

@login_required
def crear_ingrediente(request):
    if request.method == 'POST':
        form = IngredienteForm(request.POST)
        if form.is_valid():
            ingrediente = form.save()
            
            # Registrar movimiento inicial
            MovimientoInventario.objects.create(
                ingrediente=ingrediente,
                tipo='entrada',
                cantidad=ingrediente.stock_actual,
                cantidad_anterior=0,
                cantidad_nueva=ingrediente.stock_actual,
                motivo='Creación de ingrediente',
                usuario=request.user
            )
            
            messages.success(request, 'Ingrediente creado exitosamente')
            return redirect('inventario')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    return redirect('inventario')

@login_required
def editar_ingrediente(request, ingrediente_id):
    ingrediente = get_object_or_404(Ingrediente, id=ingrediente_id, activo=True)
    
    if request.method == 'POST':
        form = IngredienteForm(request.POST, instance=ingrediente)
        if form.is_valid():
            # Guardar valores anteriores para el historial
            stock_anterior = ingrediente.stock_actual
            ingrediente = form.save()
            
            # Registrar movimiento si cambió el stock
            if stock_anterior != ingrediente.stock_actual:
                MovimientoInventario.objects.create(
                    ingrediente=ingrediente,
                    tipo='ajuste',
                    cantidad=ingrediente.stock_actual - stock_anterior,
                    cantidad_anterior=stock_anterior,
                    cantidad_nueva=ingrediente.stock_actual,
                    motivo='Edición manual de stock',
                    usuario=request.user
                )
            
            messages.success(request, f'Ingrediente "{ingrediente.nombre}" actualizado exitosamente.')
            return redirect('inventario')
        else:
            # Enviar errores como mensajes flash
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
            # No redirigir, para que el modal (si se usa) pueda manejar el error
            # O si no es modal, renderizar de nuevo
    
    # Si no es POST, o si el POST falló y no es modal
    form = IngredienteForm(instance=ingrediente)
    
    # Si es AJAX request, retornar JSON con los datos (para el modal)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'id': ingrediente.id,
            'nombre': ingrediente.nombre,
            'unidad_medida': ingrediente.unidad_medida,
            'stock_actual': float(ingrediente.stock_actual),
            'stock_minimo': float(ingrediente.stock_minimo),
            'costo_unitario': float(ingrediente.costo_unitario),
            'proveedor': ingrediente.proveedor or '',
            'ubicacion': ingrediente.ubicacion or '',
            # --- ✅ LÍNEAS AÑADIDAS (por si acaso usas esta vista) ---
            'precio_paquete': float(ingrediente.precio_paquete),
            'tamaño_paquete': float(ingrediente.tamaño_paquete),
        })
    
    # Fallback para renderizado no-modal (si existe la plantilla)
    return render(request, 'inventario/editar_ingrediente.html', {
        'form': form,
        'ingrediente': ingrediente
    })
    

@login_required
def eliminar_ingrediente(request, ingrediente_id):
    ingrediente = get_object_or_404(Ingrediente, id=ingrediente_id)
    
    if request.method == 'POST':
        try:
            # Eliminar TODOS los registros relacionados
            Receta.objects.filter(ingrediente=ingrediente).delete()
            MovimientoInventario.objects.filter(ingrediente=ingrediente).delete()
            #AjusteInventario.objects.filter(ingrediente=ingrediente).delete()
            
            ingrediente.delete()
            
            messages.success(request, 'Ingrediente eliminado completamente del sistema')
        except Exception as e:
            messages.error(request, f'Error al eliminar ingrediente: {str(e)}')
    
    return redirect('inventario')

@login_required
def ajustar_inventario(request, ingrediente_id):
    ingrediente = get_object_or_404(Ingrediente, id=ingrediente_id, activo=True)
    
    if request.method == 'POST':
        form = AjusteInventarioForm(request.POST)
        if form.is_valid():
            try:
                cantidad_anterior = ingrediente.stock_actual
                cantidad_nueva = form.cleaned_data['cantidad_nueva']
                motivo = form.cleaned_data['motivo']
                
                MovimientoInventario.objects.create(
                    ingrediente=ingrediente,
                    tipo='ajuste',
                    cantidad=cantidad_nueva - cantidad_anterior,
                    cantidad_anterior=cantidad_anterior,
                    cantidad_nueva=cantidad_nueva,
                    motivo=motivo,
                    usuario=request.user
                )
                
                ingrediente.stock_actual = cantidad_nueva
                ingrediente.save()
                
                messages.success(request, 'Inventario ajustado exitosamente')
            except Exception as e:
                messages.error(request, f'Error al ajustar inventario: {str(e)}')
        else:
             for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    
    return redirect('inventario')


# ==========================================================
# ⬇️ ESTA ES LA FUNCIÓN QUE USA TU MODAL DE EDICIÓN ⬇️
# ==========================================================
@login_required
def get_ingrediente_data(request, ingrediente_id):
    """API para obtener datos de un ingrediente (AJAX)"""
    ingrediente = get_object_or_404(Ingrediente, id=ingrediente_id, activo=True)
    
    return JsonResponse({
        'id': ingrediente.id,
        'nombre': ingrediente.nombre,
        'stock_actual': float(ingrediente.stock_actual),
        'unidad_medida': ingrediente.unidad_medida,
        'stock_minimo': float(ingrediente.stock_minimo),
        'costo_unitario': float(ingrediente.costo_unitario),
        'proveedor': ingrediente.proveedor or '',
        'ubicacion': ingrediente.ubicacion or '',
        
        # --- ✅ LÍNEAS AÑADIDAS (LAS QUE FALTABAN) ---
        'precio_paquete': float(ingrediente.precio_paquete),
        'tamaño_paquete': float(ingrediente.tamaño_paquete),
    })
# ==========================================================
# ⬆️ FIN DE LA FUNCIÓN CORREGIDA ⬆️
# ==========================================================


@login_required
def agregar_receta(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        try:
            ingrediente_id = request.POST.get('ingrediente_id')
            cantidad = float(request.POST.get('cantidad'))
            
            ingrediente = get_object_or_404(Ingrediente, id=ingrediente_id)
            
            Receta.objects.create(
                producto=producto,
                ingrediente=ingrediente,
                cantidad=cantidad
            )
            
            messages.success(request, 'Ingrediente agregado a la receta')
        except Exception as e:
            messages.error(request, f'Error al agregar a receta: {str(e)}')
    
    return redirect('inventario')

@login_required
def eliminar_receta(request, receta_id):
    receta = get_object_or_404(Receta, id=receta_id)
    
    if request.method == 'POST':
        receta.delete()
        messages.success(request, 'Ingrediente eliminado de la receta')
    
    return redirect('inventario')

@login_required
def historial_inventario(request):
    movimientos = MovimientoInventario.objects.all().order_by('-fecha')
    
    context = {
        'movimientos': movimientos
    }
    return render(request, 'inventario/historial.html', context)