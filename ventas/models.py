from django.db import models
from contactos.models import Cliente
from inventario.models import Producto, PresentacionProducto

class Cotizacion(models.Model):
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('ENVIADA', 'Enviada'),
        ('ACEPTADA', 'Aceptada'),
        ('RECHAZADA', 'Rechazada'),
        ('ANULADA', 'Anulada'),
    ]
    numero = models.CharField(max_length=20, unique=True, verbose_name="Número de Cotización")
    fecha = models.DateField(verbose_name="Fecha de Cotización")
    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, verbose_name="Cliente")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Subtotal (S/.)")
    igv = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="IGV (18%) (S/.)")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Total (S/.)")
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='BORRADOR')
    notas = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"
        ordering = ['-fecha', '-numero']

    def __str__(self):
        return f"{self.numero} - {self.cliente.razon_social_nombres}"


class CotizacionDetalle(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT)
    presentacion = models.ForeignKey(PresentacionProducto, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Presentación")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unit. (S/.)")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Subtotal (S/.)")

    class Meta:
        verbose_name = "Detalle de Cotización"
        verbose_name_plural = "Detalles de Cotizaciones"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} (Cot. {self.cotizacion.numero})"


class OrdenPedido(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada / En Proceso'),
        ('DESPACHADA', 'Despachada'),
        ('ANULADA', 'Anulada'),
    ]
    numero = models.CharField(max_length=20, unique=True, verbose_name="Número de Orden de Pedido")
    fecha = models.DateField(verbose_name="Fecha de Pedido")
    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, verbose_name="Cliente")
    cotizacion_referencia = models.ForeignKey(Cotizacion, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Cotización Ref.", related_name='ordenes_pedido')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    igv = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Orden de Pedido"
        verbose_name_plural = "Órdenes de Pedido"
        ordering = ['-fecha', '-numero']

    def __str__(self):
        return self.numero


class OrdenPedidoDetalle(models.Model):
    orden = models.ForeignKey(OrdenPedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT)
    presentacion = models.ForeignKey(PresentacionProducto, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Presentación")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de Orden de Pedido"
        verbose_name_plural = "Detalles de Órdenes de Pedido"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
