from django.db import models
from ventas.models import OrdenPedido
from contactos.models import Transportista
from inventario.models import Producto

class OrdenDespacho(models.Model):
    ESTADO_CHOICES = [
        ('PROGRAMADO', 'Programado'),
        ('EN_TRANSITO', 'En Tránsito'),
        ('ENTREGADO', 'Entregado'),
        ('ANULADO', 'Anulado'),
    ]
    numero = models.CharField(max_length=20, unique=True, verbose_name="Número de Despacho")
    fecha = models.DateField(verbose_name="Fecha de Despacho")
    ordenes_pedido = models.ManyToManyField(OrdenPedido, verbose_name="Órdenes de Pedido", related_name='despachos', blank=True)
    transportista = models.ForeignKey(Transportista, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Transportista")
    direccion_origen = models.CharField(max_length=255, verbose_name="Dirección de Origen")
    direccion_destino = models.CharField(max_length=255, verbose_name="Dirección de Destino")
    peso_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Peso Total (Kg)")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PROGRAMADO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Orden de Despacho"
        verbose_name_plural = "Órdenes de Despacho"
        ordering = ['-fecha', '-numero']

    def __str__(self):
        nums = ', '.join(o.numero for o in self.ordenes_pedido.all())
        return f"{self.numero} (O.P: {nums})"

class OrdenDespachoDetalle(models.Model):
    despacho = models.ForeignKey(OrdenDespacho, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de Despacho"
        verbose_name_plural = "Detalles de Despacho"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    @property
    def peso_linea(self):
        return self.cantidad * self.producto.peso
