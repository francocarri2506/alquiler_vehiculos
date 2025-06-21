#---------------------------------MODELOS---------------------------------#
#                                                                         #
#-------------------------------------------------------------------------#
import re
import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import now


class Provincia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Departamento(models.Model):
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name='departamentos')

    class Meta:
        unique_together = ('nombre', 'provincia')

    def __str__(self):
        return f"{self.nombre} ({self.provincia})"


class Localidad(models.Model):
    nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='localidades')

    class Meta:
        unique_together = ('nombre', 'departamento')

    def __str__(self):
        return f"{self.nombre} ({self.departamento})"


class Sucursal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)

    #Usamos PROTECT para evitar que se elimine una provincia, departamento o localidad si existen sucursales que dependen de ella.
    provincia = models.ForeignKey(
        'Provincia',
        on_delete=models.PROTECT,
        related_name='sucursales'
    )

    departamento = models.ForeignKey(
        'Departamento',
        on_delete=models.PROTECT,
        related_name='sucursales'
    )

    localidad = models.ForeignKey(
        'Localidad',
        on_delete=models.PROTECT,
        related_name='sucursales'
    )

    direccion = models.TextField()

    def __str__(self):
        return f"{self.nombre} - {self.localidad}, {self.provincia}"

    #validaciones en el MODELO, la validación se aplica siempre, sin importar si se usa el modelo
    # desde un serializer, un formulario, un script, o el admin de Django

    def clean(self):
        # Validación jerárquica
        if self.departamento.provincia != self.provincia:
            raise ValidationError("El departamento no pertenece a la provincia indicada.")

        if self.localidad.departamento != self.departamento:
            raise ValidationError("La localidad no pertenece al departamento indicado.")

        # Validación de duplicado
        if Sucursal.objects.exclude(id=self.id).filter(
            nombre__iexact=self.nombre.strip(),
            provincia=self.provincia,
            departamento=self.departamento,
            localidad=self.localidad,
            direccion=self.direccion.strip()
        ).exists():
            raise ValidationError("Ya existe una sucursal con el mismo nombre y ubicación geográfica.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Marca(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

    def clean(self):
        nombre_normalizado = self.nombre.strip().lower()

        if not nombre_normalizado:
            raise ValidationError({"nombre": "El nombre no puede estar vacío."})

        if len(nombre_normalizado) < 3:
            raise ValidationError({"nombre": "El nombre debe tener al menos 3 caracteres."})

        if "marca" in nombre_normalizado:
            raise ValidationError({"nombre": "El nombre no puede contener la palabra 'marca'."})

        if not re.search(r'[a-zA-Z]', nombre_normalizado):
            raise ValidationError({"nombre": "El nombre debe contener al menos una letra."})

        if re.search(r'[^a-zA-Z0-9\s]', nombre_normalizado):
            raise ValidationError({"nombre": "El nombre no debe contener caracteres especiales."})

        if Marca.objects.exclude(pk=self.pk).filter(nombre__iexact=nombre_normalizado).exists():
            raise ValidationError({"nombre": "Ya existe una marca con este nombre."})

        # Opcional: guardar el nombre limpio sin espacios
        self.nombre = self.nombre.strip()


class TipoVehiculo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion

    def clean(self):
        descripcion_normalizada = self.descripcion.strip().lower()

        if not descripcion_normalizada:
            raise ValidationError("La descripción no puede estar vacía.")

        if len(descripcion_normalizada) < 3:
            raise ValidationError("La descripción debe tener al menos 3 caracteres.")

        if "tipo" in descripcion_normalizada:
            raise ValidationError("La descripción no puede contener la palabra 'tipo'.")

        if not re.search(r'[a-zA-Z]', descripcion_normalizada):
            raise ValidationError("La descripción debe contener al menos una letra.")

        if re.search(r'[^a-zA-Z0-9\s]', descripcion_normalizada):
            raise ValidationError("La descripción no debe contener caracteres especiales.")

        if TipoVehiculo.objects.exclude(pk=self.pk).filter(descripcion__iexact=descripcion_normalizada).exists():
            raise ValidationError("Ya existe un tipo de vehículo con esta descripción.")

        # Limpieza final (opcional)
        self.descripcion = self.descripcion.strip()

class ModeloVehiculo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name='modelos')
    tipo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT, related_name='modelos')
    es_premium = models.BooleanField(default=False, editable=False)  # Campo calculado

    class Meta:
        #unique_together = ('nombre', 'marca') # Un modelo no puede repetirse dentro de la misma marca
        #unique_together = ('nombre', 'marca', 'tipo')
        pass

    def __str__(self):
        return f"{self.marca.nombre} {self.nombre}"

    def calcular_es_premium(self):
        return self.tipo.descripcion.lower() == 'deportivo' and self.marca.nombre.lower() in ['audi', 'bmw', 'mercedes']

    def save(self, *args, **kwargs):
        self.es_premium = self.calcular_es_premium()
        super().save(*args, **kwargs)


    def clean(self):
        # Normalizar nombre
        nombre = (self.nombre or '').strip()
        marca_nombre = self.marca.nombre if self.marca else ''

        # Validaciones
        if len(nombre) < 2:
            raise ValidationError({'nombre': 'El nombre debe tener al menos 2 caracteres.'})

        if not re.search(r'[a-zA-Z]', nombre):
            raise ValidationError({'nombre': 'El nombre debe contener al menos una letra.'})

        if re.search(r'[^a-zA-Z0-9\s]', nombre):
            raise ValidationError({'nombre': 'El nombre no debe contener caracteres especiales.'})

        if nombre.lower() in ['modelo', 'vehiculo', 'tipo', 'marca']:
            raise ValidationError({'nombre': 'El nombre del modelo es demasiado genérico.'})

        if marca_nombre and marca_nombre.lower() in nombre.lower():
            raise ValidationError({'nombre': 'El nombre del modelo no debe contener el nombre de la marca.'})

        # Unicidad (nombre, marca, tipo)
        qs = ModeloVehiculo.objects.filter(
            nombre__iexact=nombre,
            marca=self.marca,
            tipo=self.tipo
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError('Ya existe un modelo con ese nombre, marca y tipo.')

        # Restricción tipo deportivo solo marcas premium
        marcas_premium = ['audi', 'bmw', 'mercedes']
        if self.tipo and self.tipo.descripcion.lower() == 'deportivo':
            if self.marca.nombre.lower() not in marcas_premium:
                raise ValidationError('Solo las marcas Audi, BMW o Mercedes pueden tener modelos deportivos.')

        # Si todo está bien, puede retornar None o no poner return

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

    def clean(self):
        año_actual = now().year

        if self.año < 1950 or self.año > año_actual:
            raise ValidationError({'año': f"El año debe estar entre 1950 y {año_actual}."})

        if self.precio_por_dia <= 0:
            raise ValidationError({'precio_por_dia': "El precio por día debe ser mayor que cero."})

        if self.modelo and self.sucursal:
            qs = Vehiculo.objects.filter(modelo=self.modelo, sucursal=self.sucursal)
            if self.pk:
                qs = qs.exclude(id=self.pk)
            if qs.count() >= 5:
                raise ValidationError("No se puede registrar más de 5 vehículos del mismo modelo en esta sucursal.")

        if self.modelo and self.año and self.modelo.tipo.descripcion.lower() == 'deportivo':
            if self.año < 1990:
                raise ValidationError("No se pueden registrar deportivos anteriores a 1990.")
            if self.precio_por_dia < 100000:
                raise ValidationError("Los vehículos deportivos no pueden tener un precio menor a 100000 por día.")


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


    def clean(self):
        if self.fecha_inicio >= self.fecha_fin:
            raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")

        if (self.fecha_fin - self.fecha_inicio).days > 30:
            raise ValidationError("La reserva no puede superar los 30 días.")

        if self.vehiculo and self.vehiculo.estado != 'disponible':
            raise ValidationError("El vehículo no está disponible para reservar.")

        reservas_conflictivas = Reserva.objects.filter(
            vehiculo=self.vehiculo,
            estado__in=['pendiente', 'confirmada'],
            fecha_inicio__lt=self.fecha_fin,
            fecha_fin__gt=self.fecha_inicio
        ).exclude(id=self.id)

        if reservas_conflictivas.exists():
            raise ValidationError("El vehículo ya tiene una reserva en ese rango de fechas.")

        alquileres_conflictivos = Alquiler.objects.filter(
            vehiculo=self.vehiculo,
            estado__in=['pendiente', 'activo'],
            fecha_inicio__lt=self.fecha_fin,
            fecha_fin__gt=self.fecha_inicio
        )
        if alquileres_conflictivos.exists():
            raise ValidationError("El vehículo ya está alquilado en ese rango de fechas.")

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






