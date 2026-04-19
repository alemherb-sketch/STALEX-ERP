from django.db import models

class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría de Producto"
        verbose_name_plural = "Categorías de Productos"

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoría")
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de Venta (S/.)")
    costo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo Equivalente (S/.)", default=0.00)
    peso = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Peso (Kg)")
    unidad_medida = models.CharField(max_length=50, default="UNIDAD", verbose_name="Unidad de Medida")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        permissions = [
            ("can_view_price", "Puede ver precios de productos y cotizaciones"),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class PresentacionProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='presentaciones')
    nombre = models.CharField(max_length=100, verbose_name="Presentación", help_text="Ej: Paquete x6, Caja x12, Display x24")
    cantidad_por_paquete = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cant. por Paquete")
    precio_paquete = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por Paquete (S/.)")

    class Meta:
        verbose_name = "Presentación de Producto"
        verbose_name_plural = "Presentaciones de Producto"
        ordering = ['cantidad_por_paquete']

    def __str__(self):
        return f"{self.nombre} ({self.cantidad_por_paquete} uds.) - S/. {self.precio_paquete}"

    @property
    def precio_unitario(self):
        if self.cantidad_por_paquete > 0:
            return self.precio_paquete / self.cantidad_por_paquete
        return 0
class Almacen(models.Model):
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Nombre del Almacén")
    ubicacion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ubicación Detallada")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Almacén"
        verbose_name_plural = "Almacenes"

    def __str__(self):
        return self.nombre

class Stock(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='stocks')
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='stocks')
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Cantidad Disponible")
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Stock en Almacén"
        verbose_name_plural = "Stocks en Almacenes"
        unique_together = ('producto', 'almacen')

    def __str__(self):
        return f"{self.producto.nombre} en {self.almacen.nombre}: {self.cantidad}"

class Kardex(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    ]
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Movimiento")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO_CHOICES)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_actual = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Saldo post-movimiento")
    motivo = models.CharField(max_length=150, verbose_name="Motivo (Venta, Compra, Ajuste, etc.)")
    referencia = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nro. Documento Referencia")

    class Meta:
        verbose_name = "Movimiento de Kardex"
        verbose_name_plural = "Kardex de Almacén"
        ordering = ['-fecha']

    def __str__(self):
        return f"KARDEX: {self.producto.nombre} | {self.tipo_movimiento} {self.cantidad} | {self.fecha.strftime('%d/%m/%Y %H:%M')}"

class MovimientoAlmacen(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name="Tipo de Movimiento")
    almacen = models.ForeignKey(Almacen, on_delete=models.RESTRICT, verbose_name="Almacén")
    motivo = models.CharField(max_length=150, verbose_name="Motivo / Concepto", help_text="Ej: Ajuste, Merma, Donación, etc.")
    referencia = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nro. Referencia")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimiento de Almacén"
        verbose_name_plural = "Movimientos de Almacén"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.tipo} - {self.motivo} ({self.fecha.strftime('%d/%m/%Y')})"

class MovimientoAlmacenDetalle(models.Model):
    movimiento = models.ForeignKey(MovimientoAlmacen, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Cantidad")

    class Meta:
        verbose_name = "Detalle de Movimiento"
        verbose_name_plural = "Detalles de Movimientos"

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"
