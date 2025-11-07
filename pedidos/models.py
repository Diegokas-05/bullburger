from django.db import models
from productos.models import Producto, Promocion
# Importa el modelo Usuario de tu app existente
from usuarios.models import Usuario 

class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('preparando', 'Preparando'),
        ('listo', 'Listo'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    TIPOS_ENTREGA = [
        ('local', 'Recoger en local'),
        ('domicilio', 'Envío a domicilio'),
    ]
    
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
    ]
    
    # Conexión directa con tu tabla de usuarios de Django
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    promocion = models.ForeignKey(Promocion, on_delete=models.SET_NULL, null=True, blank=True)
    descuento_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=50, choices=ESTADOS, default='pendiente')
    tipo_entrega = models.CharField(max_length=20, choices=TIPOS_ENTREGA, default='local')
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='efectivo')
    direccion_entrega = models.TextField(blank=True, null=True)  # Para domicilio
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    factura_pdf = models.FileField(upload_to='facturas/', blank=True, null=True)  # ✅ nuevo campo


    def __str__(self):
        return f"Pedido {self.id} - {self.usuario.email}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Detalle {self.pedido.id} - {self.producto.nombre}"