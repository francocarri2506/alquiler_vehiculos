
from datetime import date
from decimal import Decimal

from rest_framework import serializers

from .dolar import obtener_precio_dolar_blue
#from apps.alquiler.api.v1.mixins import RangoFechasVehiculoSerializerMixin
from .mixins import RangoFechasVehiculoSerializerMixin
from apps.alquiler.models import Sucursal, Marca, TipoVehiculo, Vehiculo, Alquiler, Reserva, HistorialEstadoAlquiler, \
    ModeloVehiculo

from datetime import datetime
import re   #es un módulo de Python que permite trabajar con expresiones regulares (regex).

from django.utils import timezone

import requests
from django.core.cache import cache  # opcional para cachear resultados


#-------------------------------------------------------------------------#
#                             SUCURSAL                                    #
#-------------------------------------------------------------------------#
GEORREF_BASE = "https://apis.datos.gob.ar/georef/api"
class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = '__all__'

    def validate(self, data):
        nombre = data.get('nombre', '').strip()
        provincia = data.get('provincia', '').strip()
        localidad = data.get('localidad', '').strip()
        departamento = data.get('departamento', '').strip()
        direccion = data.get('direccion', '').strip()

        # Verificar duplicados
        if Sucursal.objects.filter(
            nombre__iexact=nombre,
            provincia__iexact=provincia,
            localidad__iexact=localidad,
            departamento__iexact=departamento,
            direccion=direccion
        ).exists():
            raise serializers.ValidationError(
                "Ya existe una sucursal con el mismo nombre y ubicación geográfica."
            )

        # Validar provincia
        provincias = self._fetch("provincias", params={"campos": "nombre", "max": 100})
        nombres_prov = {p["nombre"].lower() for p in provincias}
        if provincia.lower() not in nombres_prov:
            raise serializers.ValidationError(f"La provincia '{provincia}' no es válida.")

        # Validar departamento según provincia
        departamentos = self._fetch("departamentos", params={"provincia": provincia, "campos": "nombre", "max": 500})
        nombres_dep = {d["nombre"].lower() for d in departamentos}
        if departamento.lower() not in nombres_dep:
            raise serializers.ValidationError(f"El departamento '{departamento}' no es válido para la provincia '{provincia}'.")

        # Validar localidad según provincia y departamento
        localidades = self._fetch("localidades", params={
            "provincia": provincia,
            "departamento": departamento,
            "campos": "nombre",
            "max": 1000
        })
        nombres_loc = {l["nombre"].lower() for l in localidades}
        if localidad.lower() not in nombres_loc:
            raise serializers.ValidationError(
                f"La localidad '{localidad}' no es válida para el departamento '{departamento}' en la provincia '{provincia}'."
            )

        return data

    def _fetch(self, path, params=None):
        """Hace una petición directa a la API del gobierno sin usar caché."""
        url = f"{GEORREF_BASE}/{path}"
        try:
            response = requests.get(url, params=params or {}, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "provincias" in data:
                return data["provincias"]
            elif "departamentos" in data:
                return data["departamentos"]
            elif "localidades" in data:
                return data["localidades"]
        except requests.RequestException as e:
            raise serializers.ValidationError(f"No se pudo conectar con la API de georef: {str(e)}")
        return []

#-------------------------------------------------------------------------#
#                                 MARCA                                   #
#-------------------------------------------------------------------------#
class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'

    def validate_nombre(self, value):
        nombre_normalizado = value.strip().lower()

        # No permitir vacío
        if not nombre_normalizado:
            raise serializers.ValidationError("El nombre no puede estar vacío.")

        # Longitud mínima
        if len(nombre_normalizado) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres.")

        # No debe contener la palabra "marca"
        if "marca" in nombre_normalizado:
            raise serializers.ValidationError("El nombre no puede contener la palabra 'marca'.")

        # Debe tener al menos una letra (evita 123, ###, etc.)
        if not re.search(r'[a-zA-Z]', nombre_normalizado):
            raise serializers.ValidationError("El nombre debe contener al menos una letra.")

        # Evitar caracteres especiales no alfabéticos como @, #, %, etc.
        if re.search(r'[^a-zA-Z0-9\s]', nombre_normalizado):
            raise serializers.ValidationError("El nombre no debe contener caracteres especiales.")

        # Validación de duplicados (insensible a mayúsculas/minúsculas)
        if Marca.objects.filter(nombre__iexact=nombre_normalizado).exists():
            raise serializers.ValidationError("Ya existe una marca con este nombre.")

        return value.strip()


#-------------------------------------------------------------------------#
#                                 TIPO                                    #
#-------------------------------------------------------------------------#
class TipoVehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoVehiculo
        fields = '__all__'

    def validate_descripcion(self, value):
        descripcion_normalizada = value.strip().lower()

        if not descripcion_normalizada:
            raise serializers.ValidationError("La descripción no puede estar vacía.")

        if len(descripcion_normalizada) < 3:
            raise serializers.ValidationError("La descripción debe tener al menos 3 caracteres.")

        if "tipo" in descripcion_normalizada:
            raise serializers.ValidationError("La descripción no puede contener la palabra 'tipo'.")

        if not re.search(r'[a-zA-Z]', descripcion_normalizada):
            raise serializers.ValidationError("La descripción debe contener al menos una letra.")

        if re.search(r'[^a-zA-Z0-9\s]', descripcion_normalizada):
            raise serializers.ValidationError("La descripción no debe contener caracteres especiales.")

        if TipoVehiculo.objects.filter(descripcion__iexact=descripcion_normalizada).exists():
            raise serializers.ValidationError("Ya existe un tipo de vehículo con esta descripción.")

        return value.strip()


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


    def validate_nombre(self, value):
        nombre_normalizado = value.strip()
        marca_id = self.initial_data.get('marca')

        # que sea un nombre valido de por lo menos 2 caracteres (permitido A1, A3, etc.)
        if len(nombre_normalizado) < 2:
            raise serializers.ValidationError("El nombre debe tener al menos 2 caracteres.")

        # Debe contener al menos una letra
        if not re.search(r'[a-zA-Z]', nombre_normalizado):
            raise serializers.ValidationError("El nombre debe contener al menos una letra.")

        # No debe tener caracteres especiales
        if re.search(r'[^a-zA-Z0-9\s]', nombre_normalizado):
            raise serializers.ValidationError("El nombre no debe contener caracteres especiales.")

        # No debe ser un nombre genérico
        if nombre_normalizado.lower() in ['modelo', 'vehiculo', 'tipo', 'marca']:
            raise serializers.ValidationError("El nombre del modelo es demasiado genérico.")

        # Validar que el nombre no contenga el nombre de la marca
        if marca_id:
            try:
                marca_obj = Marca.objects.get(id=marca_id)
                if marca_obj.nombre.lower() in nombre_normalizado.lower():
                    raise serializers.ValidationError(
                        "El nombre del modelo no debe contener el nombre de la marca."
                    )
            except Marca.DoesNotExist:
                pass  # Será manejado por otras validaciones

        return nombre_normalizado

    def validate(self, attrs):
        nombre = attrs.get('nombre', '').strip()
        marca = attrs.get('marca')
        tipo = attrs.get('tipo')

        # Si es actualización, obtener valores existentes
        if self.instance:
            nombre = nombre or self.instance.nombre
            marca = marca or self.instance.marca
            tipo = tipo or self.instance.tipo

        # Validación cruzada: nombre + marca + tipo
        existe = ModeloVehiculo.objects.filter(
            nombre__iexact=nombre,
            marca=marca,
            tipo=tipo
        ).exclude(id=self.instance.id if self.instance else None)

        if existe.exists():
            raise serializers.ValidationError("Ya existe un modelo con ese nombre, marca y tipo.")

        # Validación específica para marca genérica y tipo deportivo
        if marca and tipo:
            marcas_premium = ['audi', 'bmw', 'mercedes']
            if tipo.descripcion.lower() == 'deportivo' and marca.nombre.lower() not in marcas_premium:
                raise serializers.ValidationError(
                    "Solo las marcas Audi, BMW o Mercedes pueden tener modelos deportivos."
                )

        return attrs


#-------------------------------------------------------------------------#
#                                VEHICULO                                 #
#-------------------------------------------------------------------------#
class VehiculoSerializer(serializers.ModelSerializer):
    modelo_nombre = serializers.CharField(source='modelo.nombre', read_only=True)
    marca_nombre = serializers.CharField(source='modelo.marca.nombre', read_only=True)
    tipo_nombre = serializers.CharField(source='modelo.tipo.descripcion', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    precio_usd = serializers.SerializerMethodField()

    #para que el mensaje no se muestre en ingles
    patente = serializers.CharField(
        error_messages={
            "unique": "Ya existe un vehículo con esta patente.",
            "invalid": "El valor ingresado para la patente no es válido."
        }
    )
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
        tipo_cambio = obtener_precio_dolar_blue()
        if tipo_cambio:
            return round(obj.precio_por_dia / tipo_cambio, 2)
        return None
    """
    def validate_patente(self, value):
        patente_normalizada = value.strip().upper()

        # Validar formato (6 caracteres, solo letras y números)
        if not re.match(r'^[A-Z0-9]{6}$', patente_normalizada):
            raise serializers.ValidationError(
                "La patente debe tener exactamente 6 caracteres alfanuméricos (sin símbolos)."
            )
        # Validar unicidad (case-insensitive)
        if Vehiculo.objects.filter(patente__iexact=patente_normalizada).exists():
            raise serializers.ValidationError(
                "Ya existe un vehículo con esta patente."
            )
        return patente_normalizada
        """

    def validate_patente(self, value):
        patente_normalizada = value.strip().upper()

        # Validar formato (6 caracteres, solo letras y números)
        if not re.match(r'^[A-Z0-9]{6}$', patente_normalizada):
            raise serializers.ValidationError(
                "La patente debe tener exactamente 6 caracteres alfanuméricos (sin símbolos)."
            )

        # Validar unicidad (case-insensitive), ignorando si es la misma instancia
        qs = Vehiculo.objects.filter(patente__iexact=patente_normalizada)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError(
                "Ya existe un vehículo con esta patente."
            )

        return patente_normalizada


    # Validar que no se puedan registrar vehiculos de años anteriores al 1950 y tambien mayores al año actual
    def validate_año(self, value):
        año_actual = datetime.now().year

        if value < 1950 or value > año_actual:
            raise serializers.ValidationError(
                f"El año debe estar entre 1950 y {año_actual}."
            )
        return value

    #validar que el precio por dia sea mayor que cero
    def validate_precio_por_dia(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "El precio por día debe ser mayor que cero."
            )
        return value


    def validate(self, data):
        modelo = data.get('modelo')
        sucursal = data.get('sucursal')
        año = data.get('año')
        precio = data.get('precio_por_dia')

        # Validar existencia de modelo

        if isinstance(modelo, (str, int)):
            if not ModeloVehiculo.objects.filter(id=modelo).exists():
                raise serializers.ValidationError({"modelo": "El modelo Ingresado no existe."})

        # Validar existencia de sucursal

        if isinstance(sucursal, (str, int)):
            if not Sucursal.objects.filter(id=sucursal).exists():
                raise serializers.ValidationError({"sucursal": "La sucursal ingresada no existe."})

        # Validar cantidad máxima de vehículos iguales en la sucursal (por temas de disponibilidad)

        if modelo and sucursal:
            qs = Vehiculo.objects.filter(modelo=modelo, sucursal=sucursal)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.count() >= 2:
                raise serializers.ValidationError(
                    "No se puede registrar más de 5 vehículos del mismo modelo en esta sucursal."
                )

        # Validar coherencia año con tipo deportivo (ejemplo)

        if modelo and año and año < 1990 and modelo.tipo.descripcion.lower() == 'deportivo':
            raise serializers.ValidationError(
                "No se pueden registrar deportivos anteriores a 1990."
            )

        # Validar precio mínimo para vehículos deportivos
        if modelo and precio and modelo.tipo.descripcion.lower() == 'deportivo' and precio < 100000:
            raise serializers.ValidationError(
                "Los vehículos deportivos no pueden tener un precio menor a 100000 por día."
            )

        return data


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
        fecha_inicio = data['fecha_inicio']
        fecha_fin = data['fecha_fin']
        vehiculo = data['vehiculo']
        cliente = data.get('cliente')

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
            alquileres_superpuestos = alquileres_superpuestos.exclude(id=self.instance.id)

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
#                                RESERVA                                  #
#-------------------------------------------------------------------------#

######probando authenticacion

# class ReservaSerializer(serializers.ModelSerializer):
#     cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
#     vehiculo_info = serializers.SerializerMethodField()
#     sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
#     monto_total = serializers.SerializerMethodField()
#     monto_usd = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Reserva
#         fields = [
#             'id',
#             'cliente',
#             'cliente_nombre',
#             'vehiculo',
#             'vehiculo_info',
#             'sucursal',
#             'sucursal_nombre',
#             'fecha_inicio',
#             'fecha_fin',
#             'monto_total',
#             'monto_usd',
#             'estado',
#         ]
#         extra_kwargs = {
#             'sucursal': {'required': False},  # Permitimos que sea opcional
#         }
#
#     def get_vehiculo_info(self, obj):
#         return f"{obj.vehiculo.modelo.marca.nombre} {obj.vehiculo.modelo.nombre} - {obj.vehiculo.patente}"
#
#     def get_monto_total(self, obj):
#         if obj.monto_total and obj.monto_total > 0:
#             return obj.monto_total
#         dias = (obj.fecha_fin - obj.fecha_inicio).days
#         if dias < 1:
#             dias = 1
#         return dias * obj.vehiculo.precio_por_dia
#
#     def get_monto_usd(self, obj):
#         tipo_cambio = obtener_precio_dolar_blue()
#         if tipo_cambio and obj.monto_total:
#             return round(obj.monto_total / tipo_cambio, 2)
#         return "Valor del dólar no disponible"
#
#     def validate(self, data):
#         fecha_inicio = data.get('fecha_inicio')
#         fecha_fin = data.get('fecha_fin')
#         vehiculo = data.get('vehiculo')
#         cliente = data.get('cliente')
#
#         # validar fecha de inicio no sea posterior a la fecha de fin
#
#         if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
#             raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")
#
#         # validar que una reserva no exceda los 30 dias
#
#         if fecha_inicio and fecha_fin and (fecha_fin - fecha_inicio).days > 30:
#             raise serializers.ValidationError("La reserva no puede superar los 30 días.")
#
#         # validar que un vehículo se encuentre disponible
#
#         if vehiculo and vehiculo.estado != 'disponible':
#             raise serializers.ValidationError("El vehículo no está disponible para reservar.")
#
# #       if vehiculo.estado not in ['disponible', 'reservado']:
# #           raise serializers.ValidationError("El vehículo no se encuentra disponible para alquilar.")
#
#         # Si la reserva es para hoy, debe haber al menos 3 vehículos disponibles del mismo modelo
#         hoy = timezone.now().date()
#         if fecha_inicio == hoy:
#             disponibles = Vehiculo.objects.filter(
#                 modelo=vehiculo.modelo,
#                 estado='disponible'
#             ).count()
#             if disponibles < 3:
#                 raise serializers.ValidationError(
#                     "No se puede realizar una reserva para hoy. No hay suficientes vehículos disponibles del mismo modelo."
#                 )
#
#         # validar que un vehiculo no este alquilado ni reservado en esas fechas
#
#         reservas_conflictivas = Reserva.objects.filter(
#             vehiculo=vehiculo,
#             estado__in=['pendiente', 'confirmada'],
#             fecha_inicio__lt=fecha_fin,
#             fecha_fin__gt=fecha_inicio
#         ).exclude(id=self.instance.id if self.instance else None)
#
#         if reservas_conflictivas.exists():
#             raise serializers.ValidationError("El vehículo ya tiene una reserva en ese rango de fechas.")
#
#         alquileres_conflictivos = Alquiler.objects.filter(
#             vehiculo=vehiculo,
#             estado__in=['pendiente', 'activo'],
#             fecha_inicio__lt=fecha_fin,
#             fecha_fin__gt=fecha_inicio
#         )
#
#         if alquileres_conflictivos.exists():
#             raise serializers.ValidationError("El vehículo ya está alquilado en ese rango de fechas.")
#
#         #  Validar que el cliente no tenga otra reserva activa o pendiente en esas fechas
#         if cliente:
#             reservas_cliente = Reserva.objects.filter(
#                 cliente=cliente,
#                 estado__in=["pendiente", "confirmada"],
#                 fecha_inicio__lt=fecha_fin,
#                 fecha_fin__gt=fecha_inicio,
#             ).exclude(id=self.instance.id if self.instance else None)
#
#             if reservas_cliente.exists():
#                 raise serializers.ValidationError(
#                     "El cliente ya tiene una reserva activa o pendiente en ese rango de fechas.")
#
#         #  Validar que el cliente no tenga un alquiler activo o pendiente en ese rango de fechas
#
#             alquileres_cliente = Alquiler.objects.filter(
#                 cliente=cliente,
#                 estado__in=["pendiente", "activo"],
#                 fecha_inicio__lt=fecha_fin,
#                 fecha_fin__gt=fecha_inicio,
#             )
#
#             if alquileres_cliente.exists():
#                 raise serializers.ValidationError(
#                     "El cliente ya tiene un alquiler activo o pendiente en ese rango de fechas.")
#
#         return data
#
#     def calculate_monto_total(self, vehiculo, fecha_inicio, fecha_fin):
#         dias = (fecha_fin - fecha_inicio).days
#         if dias < 1:
#             dias = 1
#         return Decimal(dias) * vehiculo.precio_por_dia
#
#     def create(self, validated_data):
#         vehiculo = validated_data['vehiculo']
#         validated_data['sucursal'] = validated_data.get('sucursal') or vehiculo.sucursal
#         validated_data['monto_total'] = self.calculate_monto_total(
#             vehiculo, validated_data['fecha_inicio'], validated_data['fecha_fin']
#         )
#         return super().create(validated_data)
#
#
#     def update(self, instance, validated_data):
#         fecha_inicio = validated_data.get('fecha_inicio', instance.fecha_inicio)
#         fecha_fin = validated_data.get('fecha_fin', instance.fecha_fin)
#         vehiculo = validated_data.get('vehiculo', instance.vehiculo)
#
#         monto_total = self.calculate_monto_total(vehiculo, fecha_inicio, fecha_fin)
#         if monto_total <= 0:
#             raise serializers.ValidationError("El monto total debe ser mayor a cero.")
#         validated_data['monto_total'] = monto_total
#
#         if 'sucursal' not in validated_data:
#             validated_data['sucursal'] = vehiculo.sucursal
#
#         return super().update(instance, validated_data)


from django.contrib.auth import get_user_model
User = get_user_model()

class ReservaSerializer(serializers.ModelSerializer):
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
            'sucursal': {'required': False},  # Permitimos que sea opcional
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
        vehiculo = data.get('vehiculo') or (self.instance.vehiculo if self.instance else None)
        fecha_inicio = data.get('fecha_inicio') or (self.instance.fecha_inicio if self.instance else None)
        fecha_fin = data.get('fecha_fin') or (self.instance.fecha_fin if self.instance else None)
        cliente = data.get('cliente') or (self.instance.cliente if self.instance else None)

        #fecha_inicio = data.get('fecha_inicio')
        #fecha_fin = data.get('fecha_fin')
        #vehiculo = data.get('vehiculo')
        #cliente = data.get('cliente')
        user = self.context['request'].user

        # Control de usuario: si no es staff, se le asigna el usuario como cliente
        if not user.is_staff:
            if cliente and cliente != user:
                raise serializers.ValidationError("No puedes crear reservas para otros usuarios.")
            data['cliente'] = user  # fuerza a que sea el mismo
        else:
            # Si es staff, debe incluir el cliente
            if not cliente:
                raise serializers.ValidationError("Debes indicar el cliente al crear la reserva como administrador.")

        # validar fecha de inicio no sea posterior a la fecha de fin

        if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
            raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")

        # validar que una reserva no exceda los 30 dias

        if fecha_inicio and fecha_fin and (fecha_fin - fecha_inicio).days > 30:
            raise serializers.ValidationError("La reserva no puede superar los 30 días.")

        # validar que un vehículo se encuentre disponible

        if vehiculo and vehiculo.estado != 'disponible':
            raise serializers.ValidationError("El vehículo no está disponible para reservar.")

#       if vehiculo.estado not in ['disponible', 'reservado']:
#           raise serializers.ValidationError("El vehículo no se encuentra disponible para alquilar.")

        # Si la reserva es para hoy, debe haber al menos 3 vehículos disponibles del mismo modelo
        hoy = timezone.now().date()
        if fecha_inicio == hoy:
            disponibles = Vehiculo.objects.filter(
                modelo=vehiculo.modelo,
                estado='disponible'
            ).count()
            if disponibles < 3:
                raise serializers.ValidationError(
                    "No se puede realizar una reserva para hoy. No hay suficientes vehículos disponibles del mismo modelo."
                )

        # validar que un vehiculo no este alquilado ni reservado en esas fechas

        reservas_conflictivas = Reserva.objects.filter(
            vehiculo=vehiculo,
            estado__in=['pendiente', 'confirmada'],
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio
        ).exclude(id=self.instance.id if self.instance else None)

        if reservas_conflictivas.exists():
            raise serializers.ValidationError("El vehículo ya tiene una reserva en ese rango de fechas.")

        alquileres_conflictivos = Alquiler.objects.filter(
            vehiculo=vehiculo,
            estado__in=['pendiente', 'activo'],
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio
        )

        if alquileres_conflictivos.exists():
            raise serializers.ValidationError("El vehículo ya está alquilado en ese rango de fechas.")

        #  Validar que el cliente no tenga otra reserva activa o pendiente en esas fechas
        if cliente:
            reservas_cliente = Reserva.objects.filter(
                cliente=cliente,
                estado__in=["pendiente", "confirmada"],
                fecha_inicio__lt=fecha_fin,
                fecha_fin__gt=fecha_inicio,
            ).exclude(id=self.instance.id if self.instance else None)

            if reservas_cliente.exists():
                raise serializers.ValidationError(
                    "El cliente ya tiene una reserva activa o pendiente en ese rango de fechas.")

        #  Validar que el cliente no tenga un alquiler activo o pendiente en ese rango de fechas

            alquileres_cliente = Alquiler.objects.filter(
                cliente=cliente,
                estado__in=["pendiente", "activo"],
                fecha_inicio__lt=fecha_fin,
                fecha_fin__gt=fecha_inicio,
            )

            if alquileres_cliente.exists():
                raise serializers.ValidationError(
                    "El cliente ya tiene un alquiler activo o pendiente en ese rango de fechas.")

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





#################esta estaba funcionando 6: 45

# from django.contrib.auth import get_user_model
# User = get_user_model()
#
# class ReservaSerializer(serializers.ModelSerializer):
#     cliente = serializers.PrimaryKeyRelatedField(
#         queryset=User.objects.all(),
#         required=False  # Se validará dinámicamente según el tipo de usuario
#     )
#     cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
#     vehiculo_info = serializers.SerializerMethodField()
#     sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
#     monto_total = serializers.SerializerMethodField()
#     monto_usd = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Reserva
#         fields = [
#             'id',
#             'cliente',
#             'cliente_nombre',
#             'vehiculo',
#             'vehiculo_info',
#             'sucursal',
#             'sucursal_nombre',
#             'fecha_inicio',
#             'fecha_fin',
#             'monto_total',
#             'monto_usd',
#             'estado',
#         ]
#         extra_kwargs = {
#             'sucursal': {'required': False},
#         }
#
#     def get_vehiculo_info(self, obj):
#         return f"{obj.vehiculo.modelo.marca.nombre} {obj.vehiculo.modelo.nombre} - {obj.vehiculo.patente}"
#
#     def get_monto_total(self, obj):
#         if obj.monto_total and obj.monto_total > 0:
#             return obj.monto_total
#         dias = (obj.fecha_fin - obj.fecha_inicio).days
#         return max(dias, 1) * obj.vehiculo.precio_por_dia
#
#     def get_monto_usd(self, obj):
#         tipo_cambio = obtener_precio_dolar_blue()
#         if tipo_cambio and obj.monto_total:
#             return round(obj.monto_total / tipo_cambio, 2)
#         return "Valor del dólar no disponible"
#
#     def validate(self, data):
#         request = self.context.get('request')
#         user = request.user if request else None
#
#         # Validar cliente según permisos
#         if not data.get('cliente'):
#             if user and not user.is_staff:
#                 data['cliente'] = user
#             elif user and user.is_staff:
#                 raise serializers.ValidationError("Debe especificar el cliente para la reserva.")
#             else:
#                 raise serializers.ValidationError("Usuario no autenticado.")
#
#         elif user and not user.is_staff and data['cliente'] != user:
#             raise serializers.ValidationError("No puede crear reservas para otros usuarios.")
#
#         # Validaciones de fechas
#         fecha_inicio = data.get('fecha_inicio')
#         fecha_fin = data.get('fecha_fin')
#         vehiculo = data.get('vehiculo')
#         cliente = data.get('cliente')
#
#         if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
#             raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")
#
#         if fecha_inicio and fecha_fin and (fecha_fin - fecha_inicio).days > 30:
#             raise serializers.ValidationError("La reserva no puede superar los 30 días.")
#
#         if vehiculo and vehiculo.estado != 'disponible':
#             raise serializers.ValidationError("El vehículo no está disponible para reservar.")
#
#         hoy = timezone.now().date()
#         if fecha_inicio == hoy:
#             disponibles = Vehiculo.objects.filter(
#                 modelo=vehiculo.modelo,
#                 estado='disponible'
#             ).count()
#             if disponibles < 3:
#                 raise serializers.ValidationError("No hay suficientes vehículos disponibles del mismo modelo para hoy.")
#
#         reservas_conflictivas = Reserva.objects.filter(
#             vehiculo=vehiculo,
#             estado__in=['pendiente', 'confirmada'],
#             fecha_inicio__lt=fecha_fin,
#             fecha_fin__gt=fecha_inicio
#         ).exclude(id=self.instance.id if self.instance else None)
#
#         if reservas_conflictivas.exists():
#             raise serializers.ValidationError("El vehículo ya tiene una reserva en ese rango de fechas.")
#
#         alquileres_conflictivos = Alquiler.objects.filter(
#             vehiculo=vehiculo,
#             estado__in=['pendiente', 'activo'],
#             fecha_inicio__lt=fecha_fin,
#             fecha_fin__gt=fecha_inicio
#         )
#
#         if alquileres_conflictivos.exists():
#             raise serializers.ValidationError("El vehículo ya está alquilado en ese rango de fechas.")
#
#         reservas_cliente = Reserva.objects.filter(
#             cliente=cliente,
#             estado__in=["pendiente", "confirmada"],
#             fecha_inicio__lt=fecha_fin,
#             fecha_fin__gt=fecha_inicio,
#         ).exclude(id=self.instance.id if self.instance else None)
#
#         if reservas_cliente.exists():
#             raise serializers.ValidationError("El cliente ya tiene una reserva activa o pendiente en ese rango de fechas.")
#
#         alquileres_cliente = Alquiler.objects.filter(
#             cliente=cliente,
#             estado__in=["pendiente", "activo"],
#             fecha_inicio__lt=fecha_fin,
#             fecha_fin__gt=fecha_inicio,
#         )
#
#         if alquileres_cliente.exists():
#             raise serializers.ValidationError("El cliente ya tiene un alquiler activo o pendiente en ese rango de fechas.")
#
#         return data
#
#     def calculate_monto_total(self, vehiculo, fecha_inicio, fecha_fin):
#         dias = (fecha_fin - fecha_inicio).days
#         return Decimal(max(dias, 1)) * vehiculo.precio_por_dia
#
#     def create(self, validated_data):
#         vehiculo = validated_data['vehiculo']
#         validated_data['sucursal'] = validated_data.get('sucursal') or vehiculo.sucursal
#         validated_data['monto_total'] = self.calculate_monto_total(
#             vehiculo, validated_data['fecha_inicio'], validated_data['fecha_fin']
#         )
#         return super().create(validated_data)
#
#     def update(self, instance, validated_data):
#         fecha_inicio = validated_data.get('fecha_inicio', instance.fecha_inicio)
#         fecha_fin = validated_data.get('fecha_fin', instance.fecha_fin)
#         vehiculo = validated_data.get('vehiculo', instance.vehiculo)
#
#         monto_total = self.calculate_monto_total(vehiculo, fecha_inicio, fecha_fin)
#         if monto_total <= 0:
#             raise serializers.ValidationError("El monto total debe ser mayor a cero.")
#         validated_data['monto_total'] = monto_total
#
#         if 'sucursal' not in validated_data:
#             validated_data['sucursal'] = vehiculo.sucursal
#
#         return super().update(instance, validated_data)




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





#sucursal sin api:

# class SucursalSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Sucursal
#         fields = '__all__'
#
#     def validate(self, data):
#         nombre = data.get('nombre')
#         provincia = data.get('provincia')
#         localidad = data.get('localidad')
#         departamento = data.get('departamento')
#         direccion = data.get('direccion')
#
#         # Evitar sucursales duplicadas con mismo nombre y ubicación
#         if Sucursal.objects.filter(
#             nombre__iexact=nombre.strip(),
#             provincia__iexact=provincia.strip(),
#             localidad__iexact=localidad.strip(),
#             departamento__iexact=departamento.strip(),
#             direccion=direccion
#         ).exists():
#             raise serializers.ValidationError(
#                 "Ya existe una sucursal con el mismo nombre y ubicación geográfica en esa localidad/provincia/departamento."
#             )
#
#         return data





""" 
#funcionando antes de implementar la logica de mixins

class AlquilerSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        fecha_inicio = validated_data['fecha_inicio']
        fecha_fin = validated_data['fecha_fin']
        vehiculo = validated_data['vehiculo']

        dias = (fecha_fin - fecha_inicio).days
        monto_total = dias * vehiculo.precio_por_dia

        if monto_total <= 0:
            raise serializers.ValidationError("El monto total debe ser mayor a cero.")

        validated_data['monto_total'] = monto_total
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Si las fechas cambian, recalculamos el monto
        fecha_inicio = validated_data.get('fecha_inicio', instance.fecha_inicio)
        fecha_fin = validated_data.get('fecha_fin', instance.fecha_fin)
        vehiculo = validated_data.get('vehiculo', instance.vehiculo)

        dias = (fecha_fin - fecha_inicio).days
        monto_total = dias * vehiculo.precio_por_dia

        if monto_total <= 0:
            raise serializers.ValidationError("El monto total debe ser mayor a cero.")

        validated_data['monto_total'] = monto_total
        return super().update(instance, validated_data)



    def create(self, validated_data):

            vehiculo = validated_data['vehiculo']
            validated_data['sucursal'] = validated_data.get('sucursal') or vehiculo.sucursal

            dias = (validated_data['fecha_fin'] - validated_data['fecha_inicio']).days or 1
            validated_data['monto_total'] = dias * vehiculo.precio_por_dia

            return super().create(validated_data)

    def update(self, instance, validated_data):

        fecha_inicio = validated_data.get('fecha_inicio', instance.fecha_inicio)
        fecha_fin = validated_data.get('fecha_fin', instance.fecha_fin)
        vehiculo = validated_data.get('vehiculo', instance.vehiculo)

        dias = (fecha_fin - fecha_inicio).days or 1
        validated_data['monto_total'] = dias * vehiculo.precio_por_dia

        if 'sucursal' not in validated_data:
            validated_data['sucursal'] = vehiculo.sucursal

        return super().update(instance, validated_data)


#####implementando la logica de cambios de estados:

class AlquilerSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
    vehiculo_info = serializers.SerializerMethodField()
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    monto_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    historial_estados = HistorialEstadoAlquilerSerializer(many=True, read_only=True)

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
            'estado',
            'historial_estados',
        ]

    ESTADOS_VALIDOS = ['pendiente', 'activo', 'finalizado', 'cancelado']
    TRANSICIONES_VALIDAS = {
        'pendiente': ['activo', 'cancelado'],
        'activo': ['finalizado', 'cancelado'],
        'finalizado': [],
        'cancelado': [],
    }

    def get_vehiculo_info(self, obj):
        return f"{obj.vehiculo.marca} {obj.vehiculo.modelo}"  # Adaptalo si cambia tu modelo

    def update(self, instance, validated_data):
        estado_nuevo = validated_data.get('estado', instance.estado)
        estado_anterior = instance.estado

        # Validar transición si hay cambio de estado
        if estado_nuevo != estado_anterior:
            transiciones = self.TRANSICIONES_VALIDAS.get(estado_anterior, [])
            if estado_nuevo not in transiciones:
                raise serializers.ValidationError(
                    f"No se puede cambiar de '{estado_anterior}' a '{estado_nuevo}'. Transiciones válidas: {transiciones}"
                )

        # Continuar con la actualización normal
        instance = super().update(instance, validated_data)

        # Si hubo cambio de estado, registrar historial
        if estado_nuevo != estado_anterior:
            usuario = self.context['request'].user  # Asegurate de pasar 'context' al serializador
            HistorialEstadoAlquiler.objects.create(
                alquiler=instance,
                estado_anterior=estado_anterior,
                estado_nuevo=estado_nuevo,
                cambiado_por=usuario if isinstance(usuario, Usuario) else None
            )

        return instance

"""

