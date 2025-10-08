from django.db import models
from productos.models import Producto

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