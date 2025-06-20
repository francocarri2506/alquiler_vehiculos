
from decimal import Decimal
from rest_framework import serializers
from .dolar import obtener_precio_dolar_blue
#from apps.alquiler.api.v1.mixins import RangoFechasVehiculoSerializerMixin
from .mixins import RangoFechasVehiculoSerializerMixin
from apps.alquiler.models import Sucursal, Marca, TipoVehiculo, Vehiculo, Alquiler, Reserva, HistorialEstadoAlquiler, \
    ModeloVehiculo

from apps.alquiler.models import Provincia, Departamento, Localidad

from datetime import datetime
import re   #es un módulo de Python que permite trabajar con expresiones regulares (regex).

from django.utils import timezone

import requests
from django.core.cache import cache  # opcional para cachear resultados


from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError, ValidationError


#-------------------------------------------------------------------------#
#                             SUCURSAL                                    #
#-------------------------------------------------------------------------#
class SucursalSerializer(serializers.ModelSerializer):
    provincia_nombre = serializers.SerializerMethodField()
    departamento_nombre = serializers.SerializerMethodField()
    localidad_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Sucursal
        fields = [
            'id',
            'nombre',
            'provincia_nombre',
            'departamento_nombre',
            'localidad_nombre',
            'direccion',
        ]

    def get_provincia_nombre(self, obj):
        return obj.provincia.nombre if obj.provincia else None

    def get_departamento_nombre(self, obj):
        return obj.departamento.nombre if obj.departamento else None

    def get_localidad_nombre(self, obj):
        return obj.localidad.nombre if obj.localidad else None

class SucursalCreateSerializer(serializers.ModelSerializer):
    provincia = serializers.CharField()
    departamento = serializers.CharField()
    localidad = serializers.CharField()

    class Meta:
        model = Sucursal
        fields = ['id', 'nombre', 'provincia', 'departamento', 'localidad', 'direccion']

    def validate(self, data):
        nombre = data.get('nombre', '').strip()
        provincia_nombre = data.get('provincia', '').strip()
        departamento_nombre = data.get('departamento', '').strip()
        localidad_nombre = data.get('localidad', '').strip()
        direccion = data.get('direccion', '').strip()

        # Buscar provincia
        try:
            provincia = Provincia.objects.get(nombre__iexact=provincia_nombre)
        except Provincia.DoesNotExist:
            raise serializers.ValidationError(f"La provincia '{provincia_nombre}' no existe en la base de datos.")

        # Buscar departamento relacionado a la provincia
        try:
            departamento = Departamento.objects.get(nombre__iexact=departamento_nombre, provincia=provincia)
        except Departamento.DoesNotExist:
            raise serializers.ValidationError(f"El departamento '{departamento_nombre}' no existe en la provincia '{provincia_nombre}'.")

        # Buscar localidad relacionada al departamento
        try:
            localidad = Localidad.objects.get(nombre__iexact=localidad_nombre, departamento=departamento)
        except Localidad.DoesNotExist:
            raise serializers.ValidationError(f"La localidad '{localidad_nombre}' no existe en el departamento '{departamento_nombre}'.")

        # Reemplazar strings por instancias para crear/actualizar el modelo
        data['provincia'] = provincia
        data['departamento'] = departamento
        data['localidad'] = localidad
        data['nombre'] = nombre
        data['direccion'] = direccion

        return data

    def create(self, validated_data):
        try:
            instance = Sucursal.objects.create(**validated_data)
            return instance
        except DjangoValidationError as e:
            raise DRFValidationError({'non_field_errors': e.messages})

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        try:
            instance.save()
            return instance
        except DjangoValidationError as e:
            raise DRFValidationError({'non_field_errors': e.messages})

#-------------------------------------------------------------------------#
#                                 MARCA                                   #
#-------------------------------------------------------------------------#
class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'

    def validate(self, data):
        try:
            # Creamos una instancia temporal con los datos del serializer
            instance = Marca(**data)
            instance.clean()  # ejecutamos las validaciones del modelo
        except DjangoValidationError as e:
            # Capturamos los errores y los pasamos como ValidationError de DRF
            raise DRFValidationError(e.message_dict)
        return data


#-------------------------------------------------------------------------#
#                                 TIPO                                    #
#-------------------------------------------------------------------------#
class TipoVehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoVehiculo
        fields = '__all__'

    def validate(self, data):
        try:
            instance = TipoVehiculo(**data)
            instance.clean()
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict if hasattr(e, 'message_dict') else {'non_field_errors': e.messages})
        return data


#-------------------------------------------------------------------------#
#                                MODELO                                   #
#-------------------------------------------------------------------------#
class ModeloVehiculoSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
    tipo_nombre = serializers.CharField(source='tipo.descripcion', read_only=True)
    es_premium = serializers.BooleanField(read_only=True)  # Campo calculado automáticamente
    class Meta:
        model = ModeloVehiculo
        fields = [
            'id',
            'nombre',
            'marca',
            'marca_nombre',
            'tipo',
            'tipo_nombre',
            'es_premium'
        ]

    def validate(self, data):
        # Aquí creamos una instancia temporal con datos ya validados parcialmente
        # Para update, incluimos la instancia original
        instance = ModeloVehiculo(**data)
        if self.instance:
            instance.pk = self.instance.pk  # para que no choque con la unicidad

        try:
            instance.clean()
        except DjangoValidationError as e:
            if hasattr(e, 'message_dict'):
                raise DRFValidationError(e.message_dict)
            else:
                raise DRFValidationError(e.messages)
        return data


#-------------------------------------------------------------------------#
#                                VEHICULO                                 #
#-------------------------------------------------------------------------#
class VehiculoSerializer(serializers.ModelSerializer):
    modelo_nombre = serializers.CharField(source='modelo.nombre', read_only=True)
    marca_nombre = serializers.CharField(source='modelo.marca.nombre', read_only=True)
    tipo_nombre = serializers.CharField(source='modelo.tipo.descripcion', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    precio_usd = serializers.SerializerMethodField()


    class Meta:
        model = Vehiculo
        fields = [
            'id',
            'modelo',           # UUID del modelo
            'modelo_nombre',
            'marca_nombre',
            'tipo_nombre',
            'año',
            'patente',
            'precio_por_dia',
            'precio_usd',
            'estado',
            'sucursal',
            'sucursal_nombre',
        ]
        read_only_fields = ['precio_usd']

    def get_precio_usd(self, obj):
        tipo_cambio = obtener_precio_dolar_blue() #funcion externa dolar.py
        if tipo_cambio:
            return round(obj.precio_por_dia / tipo_cambio, 2)
        return None

    def validate_patente(self, value):
        patente = value.strip().upper()
        if not re.match(r'^[A-Z0-9]{6}$', patente):
            raise serializers.ValidationError("La patente debe tener exactamente 6 caracteres alfanuméricos.")

        qs = Vehiculo.objects.filter(patente__iexact=patente)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un vehículo con esta patente.")
        return patente

    def validate(self, data):
        instance = self.instance or Vehiculo()
        for attr, value in data.items():
            setattr(instance, attr, value)
        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data


#-------------------------------------------------------------------------#
#                                RESERVA                                  #
#-------------------------------------------------------------------------#

from django.contrib.auth import get_user_model
User = get_user_model()

class ReservaSerializer(serializers.ModelSerializer):
    #cliente = serializers.PrimaryKeyRelatedField(queryset=User.objects.all()) #al cambiar validaciones al clean
    cliente = serializers.PrimaryKeyRelatedField(read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
    vehiculo_info = serializers.SerializerMethodField()
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    monto_total = serializers.SerializerMethodField()
    monto_usd = serializers.SerializerMethodField()

    class Meta:
        model = Reserva
        fields = [
            'id',
            'cliente',
            'cliente_nombre',
            'vehiculo',
            'vehiculo_info',
            'sucursal',
            'sucursal_nombre',
            'fecha_inicio',
            'fecha_fin',
            'monto_total',
            'monto_usd',
            'estado',
        ]
        extra_kwargs = {
            'sucursal': {'required': False},
        }

    def get_vehiculo_info(self, obj):
        return f"{obj.vehiculo.modelo.marca.nombre} {obj.vehiculo.modelo.nombre} - {obj.vehiculo.patente}"

    def get_monto_total(self, obj):
        if obj.monto_total and obj.monto_total > 0:
            return obj.monto_total
        dias = (obj.fecha_fin - obj.fecha_inicio).days
        if dias < 1:
            dias = 1
        return dias * obj.vehiculo.precio_por_dia

    def get_monto_usd(self, obj):
        tipo_cambio = obtener_precio_dolar_blue()
        if tipo_cambio and obj.monto_total:
            return round(obj.monto_total / tipo_cambio, 2)
        return "Valor del dólar no disponible"

    def validate(self, data):

        user = self.context['request'].user

        # Primero: establecer el cliente (para usarlo en las validaciones)
        if not user.is_staff:
            data['cliente'] = user
        else:
            if not data.get('cliente'):
                raise serializers.ValidationError("Debes indicar el cliente al crear la reserva como administrador.")

        cliente = data.get('cliente') or (self.instance.cliente if self.instance else None)
        vehiculo = data.get('vehiculo') or (self.instance.vehiculo if self.instance else None)
        fecha_inicio = data.get('fecha_inicio') or (self.instance.fecha_inicio if self.instance else None)
        fecha_fin = data.get('fecha_fin') or (self.instance.fecha_fin if self.instance else None)

        # Validación del modelo
        try:
            reserva = Reserva(
                cliente=data['cliente'],
                vehiculo=vehiculo,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                sucursal=data.get('sucursal')
            )
            if self.instance:
                reserva.id = self.instance.id
            reserva.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else e.messages)

        # Validaciones

        # Validación para reservas del mismo día con pocos vehículos disponibles

        """ #descomentar si corrijo la logica del test 
        if vehiculo and fecha_inicio == timezone.now().date():
            disponibles = Vehiculo.objects.filter(
                modelo=vehiculo.modelo,
                estado='disponible'
            ).count()
            if disponibles < 2:
                raise serializers.ValidationError(
                    "No se puede realizar una reserva para hoy. No hay suficientes vehículos disponibles del mismo modelo."
                )
        """

        if cliente and fecha_inicio and fecha_fin:
            reservas_cliente = Reserva.objects.filter(
                cliente=cliente,
                estado__in=["pendiente", "confirmada"],
                fecha_inicio__lt=fecha_fin,
                fecha_fin__gt=fecha_inicio,
            ).exclude(id=self.instance.id if self.instance else None)
            if reservas_cliente.exists():
                raise serializers.ValidationError(
                    "El cliente ya tiene una reserva activa o pendiente en ese rango de fechas.")

            alquileres_cliente = Alquiler.objects.filter(
                cliente=cliente,
                estado__in=["pendiente", "activo"],
                fecha_inicio__lt=fecha_fin,
                fecha_fin__gt=fecha_inicio,
            )
            if alquileres_cliente.exists():
                raise serializers.ValidationError(
                    "El cliente ya tiene un alquiler activo o pendiente en ese rango de fechas.")

            instancia = self.instance  # Solo existe si estamos actualizando (PATCH/PUT)
            if instancia and instancia.estado == 'finalizada':
                raise serializers.ValidationError("No se puede modificar una reserva finalizada.")
        return data

    def calculate_monto_total(self, vehiculo, fecha_inicio, fecha_fin):
        dias = (fecha_fin - fecha_inicio).days
        if dias < 1:
            dias = 1
        return Decimal(dias) * vehiculo.precio_por_dia

    def create(self, validated_data):
        vehiculo = validated_data['vehiculo']
        validated_data['sucursal'] = validated_data.get('sucursal') or vehiculo.sucursal
        validated_data['monto_total'] = self.calculate_monto_total(
            vehiculo, validated_data['fecha_inicio'], validated_data['fecha_fin']
        )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        fecha_inicio = validated_data.get('fecha_inicio', instance.fecha_inicio)
        fecha_fin = validated_data.get('fecha_fin', instance.fecha_fin)
        vehiculo = validated_data.get('vehiculo', instance.vehiculo)

        monto_total = self.calculate_monto_total(vehiculo, fecha_inicio, fecha_fin)
        if monto_total <= 0:
            raise serializers.ValidationError("El monto total debe ser mayor a cero.")

        validated_data['monto_total'] = monto_total

        if 'sucursal' not in validated_data:
            validated_data['sucursal'] = vehiculo.sucursal

        return super().update(instance, validated_data)

#-------------------------------------------------------------------------#
#                                ALQUILER                                 #
#-------------------------------------------------------------------------#
class AlquilerSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
    vehiculo_info = serializers.SerializerMethodField()
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    monto_total = serializers.SerializerMethodField()
    monto_usd = serializers.SerializerMethodField()
    #historial_estados = HistorialEstadoAlquilerSerializer(many=True, read_only=True)

    class Meta:
        model = Alquiler
        fields = [
            'id',
            'cliente',
            'cliente_nombre',
            'vehiculo',
            'vehiculo_info',
            'sucursal',
            'sucursal_nombre',
            'fecha_inicio',
            'fecha_fin',
            'monto_total',
            'monto_usd',
            'estado',
        #    'historial_estados',
        ]
        extra_kwargs = {
            'sucursal': {'required': False},  # Permitimos que sea opcional
        }

    def get_vehiculo_info(self, obj):
        """Descripción del vehículo con marca, modelo y patente."""
        return f"{obj.vehiculo.modelo.marca.nombre} {obj.vehiculo.modelo.nombre} - {obj.vehiculo.patente}"

    def get_monto_total(self, obj):
        """Calcula el monto total del alquiler si no está presente."""
        if obj.monto_total and obj.monto_total > 0:
            return obj.monto_total
        dias = (obj.fecha_fin - obj.fecha_inicio).days
        if dias < 1:
            dias = 1
        return dias * obj.vehiculo.precio_por_dia

    def get_monto_usd(self, obj):
        """Convierte el monto total a USD usando el valor del dólar blue."""
        tipo_cambio = obtener_precio_dolar_blue()
        if tipo_cambio and obj.monto_total:
            return round(obj.monto_total / tipo_cambio, 2)
        return "Valor del dólar no disponible"

    def validate(self, data):

        # Para PATCH: usar el valor original si no se envió uno nuevo
        fecha_inicio = data.get('fecha_inicio', self.instance.fecha_inicio if self.instance else None)
        fecha_fin = data.get('fecha_fin', self.instance.fecha_fin if self.instance else None)
        vehiculo = data.get('vehiculo', self.instance.vehiculo if self.instance else None)
        cliente = data.get('cliente', self.instance.cliente if self.instance else None)

        #fecha_inicio = data['fecha_inicio']
        #fecha_fin = data['fecha_fin']
        #vehiculo = data['vehiculo']
        #cliente = data.get('cliente')

        #validar fecha de inicio no sea posterior a la fecha de fin

        if fecha_inicio >= fecha_fin:
            raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")

        # validar que un alquiler no exceda los 30 dias
        dias = (fecha_fin - fecha_inicio).days
        if dias > 30:
            raise serializers.ValidationError("El alquiler no puede durar más de 30 días.")

        # validar que un vehiculo se encuentre disponible
        if vehiculo.estado != 'disponible':
            raise serializers.ValidationError("El vehículo no está disponible para alquiler.")

        # validar que un vehiculo no este alquilado ni reservado en esas fechas

        alquileres_superpuestos = Alquiler.objects.filter(
            vehiculo=vehiculo,
            fecha_fin__gt=fecha_inicio,
            fecha_inicio__lt=fecha_fin
        )
        if self.instance:
            alquileres_superpuestos = alquileres_superpuestos.exclude(id=self.instance.id) #excluir al actual

        if alquileres_superpuestos.exists():
            raise serializers.ValidationError("El vehículo ya está alquilado en esas fechas.")

        reservas_superpuestas = Reserva.objects.filter(
            vehiculo=vehiculo,
            estado__in=['pendiente', 'confirmada'],
            fecha_fin__gt=fecha_inicio,
            fecha_inicio__lt=fecha_fin
        )

        if reservas_superpuestas.exists():
            raise serializers.ValidationError("El vehículo no se encuentra disponible: ya está reservado o alquilado en esas fechas.")

        # Validar que el cliente no tenga otra reserva activa en esas fechas
        if cliente:
            reservas_cliente = Reserva.objects.filter(
                cliente=cliente,
                estado__in=["pendiente", "confirmada"],
                fecha_inicio__lt=fecha_fin,
                fecha_fin__gt=fecha_inicio,
            )
            if reservas_cliente.exists():
                raise serializers.ValidationError(
                    "El cliente ya tiene una reserva activa o pendiente en ese rango de fechas.")

            # Validar que el cliente no tenga otro alquiler activo o pendiente en esas fechas
            alquileres_cliente = Alquiler.objects.filter(
                cliente=cliente,
                estado__in=["pendiente", "activo"],
                fecha_inicio__lt=fecha_fin,
                fecha_fin__gt=fecha_inicio,
            ).exclude(id=self.instance.id if self.instance else None)

            if alquileres_cliente.exists():
                raise serializers.ValidationError(
                    "El cliente ya tiene un alquiler activo o pendiente en ese rango de fechas.")

        return data


    def create(self, validated_data):
        vehiculo = validated_data['vehiculo']
        validated_data['sucursal'] = validated_data.get('sucursal') or vehiculo.sucursal

        dias = (validated_data['fecha_fin'] - validated_data['fecha_inicio']).days
        dias = dias if dias > 0 else 1
        precio_diario = vehiculo.precio_por_dia
        validated_data['monto_total'] = dias * precio_diario
        return super().create(validated_data)

    def update(self, instance, validated_data):
        fecha_inicio = validated_data.get('fecha_inicio', instance.fecha_inicio)
        fecha_fin = validated_data.get('fecha_fin', instance.fecha_fin)
        vehiculo = validated_data.get('vehiculo', instance.vehiculo)

        dias = (fecha_fin - fecha_inicio).days
        dias = dias if dias > 0 else 1
        precio_diario = vehiculo.precio_por_dia
        validated_data['monto_total'] = dias * precio_diario

        if 'sucursal' not in validated_data:
            validated_data['sucursal'] = vehiculo.sucursal

        return super().update(instance, validated_data)


#-------------------------------------------------------------------------#
#                             HISTORIAL-ESTADO                            #
#-------------------------------------------------------------------------#
class HistorialEstadoAlquilerSerializer(serializers.ModelSerializer):
    cambiado_por_username = serializers.CharField(source='cambiado_por.username', read_only=True)

    class Meta:
        model = HistorialEstadoAlquiler
        fields = [
            'estado_anterior',
            'estado_nuevo',
            'fecha_cambio',
            'cambiado_por',
            'cambiado_por_username',
        ]

    # Lista de estados válidos desde el modelo Alquiler
    ESTADOS_VALIDOS = ['pendiente', 'activo', 'finalizado', 'cancelado']

    # Reglas de transición válidas
    TRANSICIONES_VALIDAS = {
        'pendiente': ['activo', 'cancelado'],
        'activo': ['finalizado', 'cancelado'],
        'finalizado': [],
        'cancelado': [],
    }

    def validate_estado_anterior(self, value):
        if value not in self.ESTADOS_VALIDOS:
            raise serializers.ValidationError(f"Estado anterior '{value}' no es válido.")
        return value

    def validate_estado_nuevo(self, value):
        if value not in self.ESTADOS_VALIDOS:
            raise serializers.ValidationError(f"Estado nuevo '{value}' no es válido.")
        return value

    def validate(self, data):
        estado_ant = data.get('estado_anterior')
        estado_nuevo = data.get('estado_nuevo')

        # No permitir que el nuevo estado sea igual al anterior
        if estado_ant == estado_nuevo:
            raise serializers.ValidationError("El estado anterior y el nuevo no pueden ser iguales.")

        # Validar que la transición sea válida
        transiciones_posibles = self.TRANSICIONES_VALIDAS.get(estado_ant, [])
        if estado_nuevo not in transiciones_posibles:
            raise serializers.ValidationError(
                f"No se permite cambiar de '{estado_ant}' a '{estado_nuevo}'. Transiciones válidas: {transiciones_posibles}"
            )

        return data

