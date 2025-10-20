# inventario/models.py
from django.db import models
from django.contrib.auth import get_user_model
from productos.models import Producto

Usuario = get_user_model()

# ✅ MANTENER tus modelos existentes (para productos terminados)
class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    minimo = models.IntegerField(default=10)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inventario de {self.producto.nombre}"

class InventarioHistorial(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cambio = models.IntegerField()
    motivo = models.CharField(max_length=200)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Historial {self.producto.nombre}"

# ✅ AGREGAR nuevos modelos (para ingredientes/materias primas)
class Ingrediente(models.Model):
    UNIDADES = [
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
        ('unidad', 'Unidades'),
        ('lb', 'Libras'),
    ]
    
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.CharField(max_length=10, choices=UNIDADES)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=10)
    
    # ✅ NUEVO SISTEMA: Precio por paquete + tamaño
    precio_paquete = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Precio del Paquete"
    )
    tamaño_paquete = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=1,
        verbose_name="Tamaño del Paquete"
    )
    
    proveedor = models.CharField(max_length=100, blank=True, null=True)
    ubicacion = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.stock_actual} {self.unidad_medida})"

    # ✅ MÉTODOS CALCULADOS AUTOMÁTICAMENTE
    @property
    def costo_unitario(self):
        """Calcula automáticamente el costo por unidad de medida"""
        if self.tamaño_paquete > 0:
            return self.precio_paquete / self.tamaño_paquete
        return 0

    @property
    def estado_stock(self):
        """Determina el estado del stock: normal, bajo o agotado"""
        if self.stock_actual <= 0:
            return 'agotado'
        elif self.stock_actual <= self.stock_minimo:
            return 'bajo'
        else:
            return 'normal'

    @property
    def valor_total(self):
        """Calcula el valor total del stock del ingrediente"""
        return self.stock_actual * self.costo_unitario

    def get_costo_por_unidad_display(self):
        """Muestra el costo por unidad de forma legible"""
        return f"${self.costo_unitario:.6f} por {self.unidad_medida}"

class Receta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)  # ✅ CASCADE para eliminación completa
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    notas = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['producto', 'ingrediente']

    def __str__(self):
        return f"{self.producto.nombre} - {self.ingrediente.nombre}"

    @property
    def costo_ingrediente(self):
        """Calcula el costo de este ingrediente en la receta"""
        return self.cantidad * self.ingrediente.costo_unitario

    @property
    def hay_suficiente_stock(self):
        """Verifica si hay suficiente stock para preparar este ingrediente"""
        return self.ingrediente.stock_actual >= self.cantidad
    
class MovimientoInventario(models.Model):
    TIPOS_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    ]
    
    # ✅ CAMBIADO A CASCADE para eliminación completa
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, null=True, blank=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=15, choices=TIPOS_MOVIMIENTO)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_nueva = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=200)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.ingrediente:
            return f"{self.tipo} - {self.ingrediente.nombre} - {self.fecha}"
        else:
            return f"{self.tipo} - {self.producto.nombre} - {self.fecha}"
        
class AjusteInventario(models.Model):
    # ✅ CAMBIADO A CASCADE para eliminación completa
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_nueva = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ajuste de {self.ingrediente.nombre} por {self.usuario.username} el {self.fecha.strftime('%Y-%m-%d')}"