# productos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Producto, Categoria
from .forms import ProductoForm
from inventario.models import Ingrediente, Receta

@login_required
def lista_productos(request):
    """Vista para listar todos los productos"""
    productos = Producto.objects.all().select_related('categoria')
    categorias = Categoria.objects.all()
    ingredientes = Ingrediente.objects.filter(activo=True) 
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'ingredientes': ingredientes,
    }
    
    return render(request, 'administrador/menu.html', context)

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
            
            # Procesar la receta si hay ingredientes
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
            
            # Crear las recetas
            for ingrediente_data in ingredientes_data:
                Receta.objects.create(
                    producto=producto,
                    ingrediente_id=ingrediente_data['ingrediente_id'],
                    cantidad=ingrediente_data['cantidad']
                )
            
            messages.success(request, 'Producto creado exitosamente con su receta')
            return redirect('menu_administrador')  # ✅ CAMBIADO
            
        except Exception as e:
            messages.error(request, f'Error al crear producto: {str(e)}')
    
    return redirect('menu_administrador')  # ✅ CAMBIADO

@login_required
def editar_producto(request, producto_id):
    """Vista para editar un producto existente"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto = form.save()
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('menu_administrador')  # ✅ CAMBIADO
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
        if nombre:
            # Verificar si ya existe
            if Categoria.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, 'Ya existe una categoría con ese nombre')
            else:
                Categoria.objects.create(nombre=nombre)
                messages.success(request, 'Categoría creada exitosamente')
        else:
            messages.error(request, 'El nombre de la categoría es requerido')
    
    return redirect('menu_administrador')  # ✅ CAMBIADO

@login_required
def eliminar_categoria(request, categoria_id):
    """Vista para eliminar una categoría"""
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if request.method == 'POST':
        # Verificar si hay productos usando esta categoría
        productos_count = Producto.objects.filter(categoria=categoria).count()
        
        if productos_count > 0:
            messages.error(request, 'No se puede eliminar una categoría que tiene productos asociados')
        else:
            categoria.delete()
            messages.success(request, 'Categoría eliminada exitosamente')
    
    return redirect('menu_administrador')  # ✅ CAMBIADO

# views.py
from django.shortcuts import render
from .models import Categoria, Producto

def menu_cliente(request):
    categorias = Categoria.objects.all().order_by('nombre')
    productos = Producto.objects.filter(disponible=True).select_related('categoria')
    return render(request, 'cliente/menu_cliente.html', {
        'categorias': categorias,
        'productos': productos
    })
