from django.db import models
from productos.models import Producto, Promocion
from usuarios.models import Usuario
from django.conf import settings
from django.core.files.storage import default_storage
import os


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

    # Relaciones y datos principales
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    promocion = models.ForeignKey(Promocion, on_delete=models.SET_NULL, null=True, blank=True)

    descuento_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=50, choices=ESTADOS, default='pendiente')
    tipo_entrega = models.CharField(max_length=20, choices=TIPOS_ENTREGA, default='local')
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='efectivo')
    direccion_entrega = models.TextField(blank=True, null=True)  # Solo para domicilio

    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    # Archivo de factura (guardar SIEMPRE con nombre relativo, p.ej. "facturas/factura_123.pdf")
    factura_pdf = models.FileField(upload_to='facturas/', blank=True, null=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.usuario.email}"

    # ===== Utilidades de factura =====
    @property
    def factura_disponible(self) -> bool:
        """
        Devuelve True si hay un archivo asociado y realmente existe en el storage
        o en el sistema de archivos. Soporta casos donde en la base quedó
        'media/' duplicado o incluso una ruta absoluta.
        """
        f = self.factura_pdf
        if not f:
            return False

        try:
            # Nombre relativo al storage (lo ideal)
            name = (f.name or "").strip().lstrip("/").replace("\\", "/")
            if name.startswith("media/"):
                # Corrige registros antiguos con 'media/' duplicado
                name = name[6:]

            # 1) Chequeo en el storage configurado (lo normal)
            if name and default_storage.exists(name):
                return True

            # 2) Chequeo directo por path absoluto (por si guardaron la ruta completa)
            #    Si f.path no existe, construimos: MEDIA_ROOT / name
            path = getattr(f, "path", None)
            if not path:
                path = os.path.join(settings.MEDIA_ROOT, name)

            return os.path.exists(path)
        except Exception:
            # Si algo falla, consideramos que no está disponible
            return False

    @property
    def factura_url(self):
        """
        Devuelve la URL lista para usar en la plantilla SOLO si la factura existe.
        Si no existe, devuelve None.
        """
        if self.factura_disponible and self.factura_pdf:
            try:
                return self.factura_pdf.url
            except Exception:
                return None
        return None


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Detalle {self.pedido.id} - {self.producto.nombre}"
