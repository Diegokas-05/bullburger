# En productos/views.py - AÑADE estas vistas
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Producto, Categoria
from .forms import ProductoForm

@login_required
def lista_productos(request):
    """Vista para listar todos los productos"""
    productos = Producto.objects.all().select_related('categoria')
    categorias = Categoria.objects.all()
    
    return render(request, 'administrador/menu.html', {
        'productos': productos,
        'categorias': categorias
    })

@login_required
def crear_producto(request):
    """Vista para crear un nuevo producto"""
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)  # Añade request.FILES para imágenes
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" creado exitosamente!')
            return redirect('lista_productos')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ProductoForm()
    
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'administrador/menu.html', {
        'form': form,
        'productos': productos,
        'categorias': categorias
    })

@login_required
def editar_producto(request, producto_id):
    """Vista para editar un producto existente"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado exitosamente!')
            return redirect('lista_productos')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ProductoForm(instance=producto)
    
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'administrador/menu.html', {
        'form': form,
        'producto_editar': producto,
        'productos': productos,
        'categorias': categorias
    })

@login_required
def eliminar_producto(request, producto_id):
    """Vista para eliminar un producto"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        nombre_producto = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado exitosamente!')
        return redirect('lista_productos')
    
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'administrador/menu.html', {
        'producto_eliminar': producto,
        'productos': productos,
        'categorias': categorias
    })

@login_required
def crear_categoria(request):
    """Vista para crear una nueva categoría"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            # Verificar si ya existe
            if Categoria.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, f'La categoría "{nombre}" ya existe.')
            else:
                categoria = Categoria.objects.create(nombre=nombre)
                messages.success(request, f'Categoría "{nombre}" creada exitosamente!')
        else:
            messages.error(request, 'El nombre de la categoría es requerido.')
    
    return redirect('lista_productos')

@login_required
def eliminar_categoria(request, categoria_id):
    """Vista para eliminar una categoría"""
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if request.method == 'POST':
        # Verificar si hay productos usando esta categoría
        productos_count = Producto.objects.filter(categoria=categoria).count()
        
        if productos_count > 0:
            messages.error(request, f'No se puede eliminar la categoría "{categoria.nombre}" porque tiene {productos_count} producto(s) asociado(s).')
        else:
            nombre_categoria = categoria.nombre
            categoria.delete()
            messages.success(request, f'Categoría "{nombre_categoria}" eliminada exitosamente!')
    
    return redirect('lista_productos')