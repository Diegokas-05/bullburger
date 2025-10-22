# inventario/management/commands/poblar_ingredientes_wendys.py
import os
import django
from django.core.management.base import BaseCommand
from inventario.models import CategoriaIngrediente, IngredienteHamburguesa, Ingrediente, Complemento

class Command(BaseCommand):
    help = 'Pobla la base de datos con ingredientes estilo Wendy\'s'

    def handle(self, *args, **options):
        # Crear categorías
        categorias_data = [
            ('Salsas', 'Salsas y aderezos', 1),
            ('Verduras', 'Verduras y vegetales', 2),
            ('Quesos', 'Tipos de queso', 3),
            ('Carnes', 'Carnes y proteínas', 4),
            ('Extras', 'Ingredientes adicionales', 5),
        ]
        
        categorias = {}
        for nombre, desc, orden in categorias_data:
            categoria, created = CategoriaIngrediente.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': desc, 'orden': orden}
            )
            categorias[nombre] = categoria
        
        # Ingredientes base (que se pueden quitar)
        ingredientes_base = [
            ('Mayonesa', 'Salsas', 'salsa', 0),
            ('Ketchup', 'Salsas', 'salsa', 0),
            ('Pepinillo', 'Verduras', 'base', 0),
            ('Cebolla', 'Verduras', 'base', 0),
            ('Tomate', 'Verduras', 'base', 0),
            ('Lechuga', 'Verduras', 'base', 0),
            ('Tocino', 'Carnes', 'base', 0),
            ('Lasca Queso Americano', 'Quesos', 'base', 0),
        ]
        
        # Ingredientes extra
        ingredientes_extra = [
            ('Extra Pepinillo', 'Verduras', 'extra', 0.25),
            ('Extra Cebolla', 'Verduras', 'extra', 0.25),
            ('Extra Tomate', 'Verduras', 'extra', 0.25),
            ('Extra Lechuga', 'Verduras', 'extra', 0.25),
            ('Extra Lechuga Romana', 'Verduras', 'extra', 0.25),
            ('Extra Lasca de Queso Americano', 'Quesos', 'extra', 0.50),
            ('Extra Tocino', 'Carnes', 'extra', 1.00),
            ('Extra Bacon Bits', 'Extras', 'extra', 1.00),
            ('Extra Carne 4 Oz', 'Carnes', 'extra', 1.25),
        ]
        
        # Crear ingredientes base
        for nombre, categoria_nombre, tipo, precio in ingredientes_base:
            categoria = categorias[categoria_nombre]
            IngredienteHamburguesa.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'categoria': categoria,
                    'tipo': tipo,
                    'precio_extra': precio
                }
            )
        
        # Crear ingredientes extra
        for nombre, categoria_nombre, tipo, precio in ingredientes_extra:
            categoria = categorias[categoria_nombre]
            IngredienteHamburguesa.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'categoria': categoria,
                    'tipo': tipo,
                    'precio_extra': precio
                }
            )
        
        # Crear complementos (papas fritas)
        Complemento.objects.get_or_create(
            nombre='Papas Fritas',
            tamano='normal',
            defaults={'tipo': 'papas', 'precio': 0}
        )
        Complemento.objects.get_or_create(
            nombre='Papas Fritas',
            tamano='mediano',
            defaults={'tipo': 'papas', 'precio': 0.75}
        )
        Complemento.objects.get_or_create(
            nombre='Papas Fritas',
            tamano='grande',
            defaults={'tipo': 'papas', 'precio': 1.00}
        )
        
        self.stdout.write(
            self.style.SUCCESS('✅ Ingredientes estilo Wendy\'s creados exitosamente!')
        )