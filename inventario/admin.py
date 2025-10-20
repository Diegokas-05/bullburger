# inventario/admin.py
from django.contrib import admin
from .models import Inventario, InventarioHistorial, Ingrediente, Receta, MovimientoInventario,AjusteInventario

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ['producto', 'stock', 'minimo']
    list_filter = ['producto__categoria']

@admin.register(InventarioHistorial)
class InventarioHistorialAdmin(admin.ModelAdmin):
    list_display = ['producto', 'cambio', 'motivo', 'creado_en']
    list_filter = ['creado_en']

@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'unidad_medida', 'stock_actual', 'stock_minimo', 'costo_unitario', 'estado_stock', 'valor_total']
    list_filter = ['unidad_medida', 'activo']
    search_fields = ['nombre', 'proveedor']

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'ingrediente', 'cantidad', 'costo_ingrediente']
    list_filter = ['producto__categoria', 'ingrediente']
    search_fields = ['producto__nombre', 'ingrediente__nombre']

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ['ingrediente', 'tipo', 'cantidad', 'cantidad_anterior', 'cantidad_nueva', 'usuario', 'fecha']
    list_filter = ['tipo', 'fecha', 'ingrediente']
    search_fields = ['ingrediente__nombre', 'motivo']
    readonly_fields = ['fecha']

 #ELIMINA esta parte si no tienes el modelo AjusteInventario
@admin.register(AjusteInventario)
class AjusteInventarioAdmin(admin.ModelAdmin):
    list_display = ['ingrediente', 'cantidad_anterior', 'cantidad_nueva', 'usuario', 'fecha']    
    list_filter = ['fecha', 'ingrediente']
    readonly_fields = ['fecha']