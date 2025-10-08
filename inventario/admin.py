from django.contrib import admin
from .models import Inventario, InventarioHistorial

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ['producto', 'stock', 'minimo']
    list_filter = ['producto__categoria']

@admin.register(InventarioHistorial)
class InventarioHistorialAdmin(admin.ModelAdmin):
    list_display = ['producto', 'cambio', 'motivo', 'creado_en']
    list_filter = ['creado_en']