from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)  # ← NUEVO CAMPO
    imagen_url = models.URLField(blank=True, null=True)  
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    disponible = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
    
    def calcular_costo_produccion(self):
        """Calcula el costo automáticamente basado en los ingredientes"""
        total = 0
        for receta in self.receta_set.all():
            total += receta.cantidad * receta.ingrediente.costo_unitario
        return total
    
    @property
    def is_currently_available(self):
        """
        VERIFICACIÓN DE DISPONIBILIDAD EN TIEMPO REAL:
        Comprueba si el admin lo marcó como disponible Y
        si TODOS los ingredientes tienen stock 'normal'.
        """
        # 1. Chequeo del estado manual del administrador
        if not self.disponible:
            return False
            
        # 2. Chequeo de stock basado en la receta
        # (Usamos prefetch_related en la VISTA para optimizar esto)
        recetas = self.receta_set.all().select_related('ingrediente')

        # Si no tiene receta (ej. una Coca-Cola), está disponible.
        if not recetas.exists():
            return True

        for receta in recetas:
            # Obtenemos el estado ('normal', 'bajo', 'agotado') del ingrediente
            # Asumimos que tu modelo Ingrediente tiene la propiedad @property estado_stock
            ingrediente_status = receta.ingrediente.estado_stock

            # Si CUALQUIER ingrediente está 'bajo' o 'agotado',
            # el producto completo NO está disponible.
            if ingrediente_status == 'bajo' or ingrediente_status == 'agotado':
                return False
                
        # Si pasó el bucle y todos los ingredientes están 'normal',
        # el producto SÍ está disponible.
        return True
    
class Promocion(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField()
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descuento_fijo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.codigo

from django.db import models
from django.conf import settings
from .models import Producto  # asegúrate de importar correctamente el modelo Producto

class CarritoItem(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    agregado_en = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return self.cantidad * self.producto.precio

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} ({self.usuario.email})"
