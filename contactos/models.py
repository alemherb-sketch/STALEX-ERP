from django.db import models

class Cliente(models.Model):
    TIPO_DOC_CHOICES = [
        ('DNI', 'DNI'),
        ('RUC', 'RUC'),
        ('CE', 'Carné de Extranjería'),
    ]
    tipo_documento = models.CharField(max_length=3, choices=TIPO_DOC_CHOICES, default='DNI')
    numero_documento = models.CharField(max_length=20, unique=True)
    razon_social_nombres = models.CharField(max_length=200, verbose_name="Razón Social / Nombres")
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"{self.numero_documento} - {self.razon_social_nombres}"

class Proveedor(models.Model):
    ruc = models.CharField(max_length=11, unique=True, verbose_name="RUC")
    razon_social = models.CharField(max_length=200, verbose_name="Razón Social")
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico")
    contacto = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nombre de Contacto")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return f"{self.ruc} - {self.razon_social}"

class Transportista(models.Model):
    TIPO_DOC_CHOICES = [
        ('DNI', 'DNI'),
        ('RUC', 'RUC'),
    ]
    tipo_documento = models.CharField(max_length=3, choices=TIPO_DOC_CHOICES, default='RUC')
    numero_documento = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200, verbose_name="Nombre o Razón Social")
    placa_vehiculo = models.CharField(max_length=15, verbose_name="Placa del Vehículo", blank=True, null=True)
    licencia_conducir = models.CharField(max_length=20, verbose_name="Licencia de Conducir", blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transportista"
        verbose_name_plural = "Transportistas"

    def __str__(self):
        return f"{self.nombre} ({self.placa_vehiculo})"
