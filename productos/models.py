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
