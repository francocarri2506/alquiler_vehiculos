
import uuid
from django.db import models
from django.conf import settings


class Sucursal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    localidad = models.CharField(max_length=100)
    direccion = models.TextField()

    def __str__(self):
        return f"{self.nombre} - {self.localidad}, {self.provincia}"

class Marca(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class TipoVehiculo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion


"""
class Vehiculo(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('alquilado', 'Alquilado'),
        ('mantenimiento', 'En mantenimiento'),
        ('reservado', 'Reservado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name='vehiculos')
    modelo = models.CharField(max_length=100)
    patente = models.CharField(max_length=20, unique=True)
    tipo = models.ForeignKey(TipoVehiculo, on_delete=models.SET_NULL, null=True)
    año = models.PositiveIntegerField()
    precio_por_dia = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    sucursal = models.ForeignKey('Sucursal', on_delete=models.CASCADE, related_name='vehiculos')

    def __str__(self):
        return f"{self.marca.nombre} {self.modelo} ({self.patente})"



"""






#-------------------------MEJORA EN MODELOS-------------------------------#
#                                                                         #
#-------------------------------------------------------------------------#


class ModeloVehiculo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name='modelos')
    tipo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT, related_name='modelos')
    es_premium = models.BooleanField(default=False, editable=False)  # Campo calculado

    class Meta:
        unique_together = ('nombre', 'marca') # Un modelo no puede repetirse dentro de la misma marca

    def __str__(self):
        return f"{self.marca.nombre} {self.nombre}"

    def calcular_es_premium(self):
        return self.tipo.descripcion.lower() == 'deportivo' and self.marca.nombre.lower() in ['audi', 'bmw', 'mercedes']

    def save(self, *args, **kwargs):
        self.es_premium = self.calcular_es_premium()
        super().save(*args, **kwargs)


class Vehiculo(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('alquilado', 'Alquilado'),
        ('mantenimiento', 'En mantenimiento'),
        ('reservado', 'Reservado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    modelo = models.ForeignKey(ModeloVehiculo, on_delete=models.CASCADE, related_name='vehiculos')

    #modelo = models.ForeignKey(ModeloVehiculo, null=True, on_delete=models.SET_NULL)
    patente = models.CharField(max_length=20, unique=True)
    año = models.PositiveIntegerField()
    precio_por_dia = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name='vehiculos')

    """
    def __str__(self):
        return f"{self.modelo.marca.nombre} {self.modelo.nombre} ({self.patente})"
    """
    def __str__(self):
        return f"{self.modelo.marca.nombre} {self.modelo.nombre} - {self.patente}"

    @property
    def tipo(self):
        return self.modelo.tipo


#-------------------------MEJORA EN MODELOS-------------------------------#
#                                                                         #
#-------------------------------------------------------------------------#


class Alquiler(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('activo', 'Activo'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alquileres')
    vehiculo = models.ForeignKey('Vehiculo', on_delete=models.CASCADE, related_name='alquileres')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.SET_NULL, null=True, blank=True, related_name='alquileres')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')

    def __str__(self):
        return f"Alquiler {self.id} - {self.cliente}"

class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservas')
    vehiculo = models.ForeignKey('Vehiculo', on_delete=models.CASCADE, related_name='reservas')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"Reserva {self.id} - {self.cliente}"


class HistorialEstadoAlquiler(models.Model):
    alquiler = models.ForeignKey(Alquiler, on_delete=models.CASCADE, related_name='historial_estados')
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    #cambiado_por = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    cambiado_por = models.ForeignKey('usuario.Usuario', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.alquiler.id} | {self.estado_anterior} → {self.estado_nuevo} ({self.fecha_cambio})"




"""


"""

