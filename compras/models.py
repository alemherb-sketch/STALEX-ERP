from django.db import models
from contactos.models import Proveedor
from inventario.models import Producto, PresentacionProducto

class OrdenCompra(models.Model):
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('SOLICITADA', 'Solicitada'),
        ('RECIBIDA', 'Recibida'),
        ('ANULADA', 'Anulada'),
    ]
    numero = models.CharField(max_length=20, unique=True, verbose_name="Número de Orden")
    fecha = models.DateField(verbose_name="Fecha de Orden")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.RESTRICT, verbose_name="Proveedor")
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='BORRADOR')
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    igv = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    notas = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"
        ordering = ['-fecha', '-numero']

    def __str__(self):
        return f"{self.numero} - {self.proveedor.razon_social}"

class OrdenCompraDetalle(models.Model):
    orden = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT)
    presentacion = models.ForeignKey(PresentacionProducto, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Presentación")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo Unitario (S/.)")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de Orden de Compra"
        verbose_name_plural = "Detalles de Orden de Compra"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
