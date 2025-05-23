
from datetime import date
from rest_framework import serializers

from .dolar import obtener_precio_dolar_blue
#from apps.alquiler.api.v1.mixins import RangoFechasVehiculoSerializerMixin
from .mixins import RangoFechasVehiculoSerializerMixin
from apps.alquiler.models import Sucursal, Marca, TipoVehiculo, Vehiculo, Alquiler, Reserva, HistorialEstadoAlquiler, \
    ModeloVehiculo

from datetime import datetime
import re   #es un módulo de Python que permite trabajar con expresiones regulares (regex).


class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = '__all__'

    def validate(self, data):
        nombre = data.get('nombre')
        provincia = data.get('provincia')
        localidad = data.get('localidad')
        departamento = data.get('departamento')
        direccion = data.get('direccion')

        # Evitar sucursales duplicadas con mismo nombre y ubicación
        if Sucursal.objects.filter(
            nombre__iexact=nombre.strip(),
            provincia__iexact=provincia.strip(),
            localidad__iexact=localidad.strip(),
            departamento__iexact=departamento.strip(),
            direccion=direccion
        ).exists():
            raise serializers.ValidationError(
                "Ya existe una sucursal con el mismo nombre y ubicación geográfica en esa localidad/provincia/departamento."
            )

        return data


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


"""
#vehiculo viejo, se muestra bien, pero no tiene relacion con los datos


class VehiculoSerializer(serializers.ModelSerializer):
    marca = serializers.CharField(source='marca.nombre', read_only=True)
    tipo = serializers.CharField(source='tipo.descripcion', read_only=True)
    sucursal = serializers.CharField(source='sucursal.nombre', read_only=True)

    class Meta:
        model = Vehiculo
        fields = [
            'id',
            'marca',
            'modelo',
            'patente',
            'tipo',
            'año',
            'precio_por_dia',
            'estado',
            'sucursal',
        ]


    def validate_patente(self, value):
        patente_normalizada = value.strip().upper()

        # Validar formato (6 caracteres, solo letras y números)
        if not re.match(r'^[A-Z0-9]{6}$', patente_normalizada): #Si no coincide (not re.match(...)), entonces lanzamos un error
            raise serializers.ValidationError(
                "La patente debe tener exactamente 6 caracteres alfanuméricos en mayúsculas (sin símbolos)."
            )

        # Validar unicidad (case-insensitive)
        if Vehiculo.objects.filter(patente__iexact=patente_normalizada).exists():
            raise serializers.ValidationError("Ya existe un vehículo con esta patente.")

        return patente_normalizada

    def validate_anio(self, value):
        año_actual = datetime.now().year
        if value < 1950 or value > año_actual:
            raise serializers.ValidationError(f"El año debe estar entre 1950 y {año_actual}.")
        return value


    def validate(self, data):
        marca = data.get('marca')
        tipo = data.get('tipo')
        sucursal = data.get('sucursal')

        #if not marca:
        #    raise serializers.ValidationError({'marca': 'Este campo es requerido.'})

        if not Marca.objects.filter(id=marca.id).exists():
            raise serializers.ValidationError("La marca especificada no existe.")

        if not TipoVehiculo.objects.filter(id=tipo.id).exists():
            raise serializers.ValidationError("El tipo de vehículo especificado no existe.")

        if not Sucursal.objects.filter(id=sucursal.id).exists():
            raise serializers.ValidationError("La sucursal especificada no existe.")

        return data

"""


"""
# #VEHICULO FUNCIONANDO, SI NO FUNCIONA EL CAMBIO DE LOS MODELOS, ESTE EL CORRECTO 18/5/ A LAS 9AM
# 
# class VehiculoSerializer(serializers.ModelSerializer):
#     # Campos para mostrar el nombre junto al UUID
#     marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
#     tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True)
#     sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
# 
#     class Meta:
#         model = Vehiculo
#         fields = [
#             'id',
#             'marca',          # UUID de marca (relación)
#             'marca_nombre',   # Nombre de la marca (solo lectura)
#             'tipo',           # UUID de tipo (relación)
#             'tipo_nombre',    # Nombre del tipo (solo lectura)
#             'modelo',
#             'año',
#             'patente',
#             'precio_por_dia',
#             'sucursal',       # UUID de sucursal (relación)
#             'sucursal_nombre' # Nombre de la sucursal (solo lectura)
#         ]
# 
#     def validate_patente(self, value):
#         patente_normalizada = value.strip().upper()
# 
#         # Validar formato (6 caracteres, solo letras y números)
#         if not re.match(r'^[A-Z0-9]{6}$', patente_normalizada):
#             raise serializers.ValidationError(
#                 "La patente debe tener exactamente 6 caracteres alfanuméricos en mayúsculas (sin símbolos)."
#             )
# 
#         # Validar unicidad (case-insensitive)
#         if Vehiculo.objects.filter(patente__iexact=patente_normalizada).exists():
#             raise serializers.ValidationError("Ya existe un vehículo con esta patente.")
# 
#         return patente_normalizada
# 
#     def validate_año(self, value):
#         año_actual = datetime.now().year
#         if value < 1950 or value > año_actual:
#             raise serializers.ValidationError(f"El año debe estar entre 1950 y {año_actual}.")
#         return value
# 
#     def validate(self, data):
#         marca = data.get('marca')
#         tipo = data.get('tipo')
#         sucursal = data.get('sucursal')
# 
#         # Validar que las relaciones existan (solo si vienen como UUID)
#         if isinstance(marca, (str, int)):
#             if not Marca.objects.filter(id=marca).exists():
#                 raise serializers.ValidationError({"marca": "La marca seleccionada no existe."})
#         if isinstance(tipo, (str, int)):
#             if not TipoVehiculo.objects.filter(id=tipo).exists():
#                 raise serializers.ValidationError({"tipo": "El tipo de vehículo seleccionado no existe."})
#         if isinstance(sucursal, (str, int)):
#             if not Sucursal.objects.filter(id=sucursal).exists():
#                 raise serializers.ValidationError({"sucursal": "La sucursal seleccionada no existe."})
# 
#         # Validar unicidad de patente en update
#         patente = data.get('patente')
#         vehiculo_id = self.instance.id if self.instance else None
#         if Vehiculo.objects.filter(patente=patente).exclude(id=vehiculo_id).exists():
#             raise serializers.ValidationError({"patente": "La patente ya está registrada para otro vehículo."})
# 
#         return data
"""

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



"""
#serializer con validaciones basicas

class AlquilerSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
    vehiculo_info = serializers.SerializerMethodField()
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
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
            'historial_estados'
        ]

    def get_vehiculo_info(self, obj):
        return f"{obj.vehiculo.marca.nombre} {obj.vehiculo.modelo} - {obj.vehiculo.patente}"

# -------------------------VALIDACIONES-----------------------------------#
#                                                                         #
# ------------------------------------------------------------------------#

    def validate(self, data):
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        vehiculo = data.get('vehiculo')

        # Fecha fin posterior a inicio
        if fecha_fin and fecha_inicio and fecha_fin <= fecha_inicio:
            raise serializers.ValidationError("La fecha de fin debe ser posterior a la de inicio.")

        # Validar que el vehículo no esté ya alquilado en ese rango
        if Alquiler.objects.filter(
                vehiculo=vehiculo,
                fecha_inicio__lt=fecha_fin,
                fecha_fin__gt=fecha_inicio,
        ).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("El vehículo ya está alquilado en esas fechas.")

        return data

class ReservaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
    vehiculo_info = serializers.SerializerMethodField()
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)

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
            'estado'
        ]

    def get_vehiculo_info(self, obj):
        return f"{obj.vehiculo.marca.nombre} {obj.vehiculo.modelo} - {obj.vehiculo.patente}"

# -------------------------VALIDACIONES-----------------------------------#
#                                                                         #
# ------------------------------------------------------------------------#

    #Validar que el cliente no tenga más de 3 reservas pendientes
    def validate(self, data):
        cliente = data.get('cliente')
        reservas_activas = Reserva.objects.filter(cliente=cliente, estado='pendiente').count()

        if reservas_activas >= 3:
            raise serializers.ValidationError("El cliente ya tiene 3 reservas pendientes.")

        return data

"""


""" 
#funcionando antes de implementar la logica de mixins

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

    def get_vehiculo_info(self, obj):
        return f"{obj.vehiculo.marca.nombre} {obj.vehiculo.modelo} - {obj.vehiculo.patente}"

    def validate(self, data):
        cliente = data.get('cliente')
        vehiculo = data.get('vehiculo')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')

        # Validar fechas
        if fecha_inicio < date.today():
            raise serializers.ValidationError("La fecha de inicio no puede ser anterior a hoy.")

        if fecha_fin <= fecha_inicio:
            raise serializers.ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")

        # Validar que el cliente no tenga un alquiler pendiente o activo
        alquileres_activos = Alquiler.objects.filter(
            cliente=cliente,
            estado__in=['pendiente', 'activo']
        ).exclude(id=self.instance.id if self.instance else None)

        if alquileres_activos.exists():
            raise serializers.ValidationError("El cliente ya tiene un alquiler pendiente o activo.")

        # Validar disponibilidad del vehículo
        if Alquiler.objects.filter(
            vehiculo=vehiculo,
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio,
        ).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("El vehículo no está disponible en el rango de fechas seleccionado.")

        return data

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



class ReservaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
    vehiculo_info = serializers.SerializerMethodField()
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    monto_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

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
            'estado',
        ]

    def get_vehiculo_info(self, obj):
        return f"{obj.vehiculo.marca.nombre} {obj.vehiculo.modelo} - {obj.vehiculo.patente}"

    def validate(self, data):
        cliente = data.get('cliente')
        vehiculo = data.get('vehiculo')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')

        if fecha_inicio < date.today():
            raise serializers.ValidationError("La fecha de inicio no puede ser anterior a hoy.")

        if fecha_fin <= fecha_inicio:
            raise serializers.ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")

        # Validar que el vehículo no esté reservado en ese rango
        reservas_conflictivas = Reserva.objects.filter(
            vehiculo=vehiculo,
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio,
        ).exclude(id=self.instance.id if self.instance else None)

        if reservas_conflictivas.exists():
            raise serializers.ValidationError("El vehículo ya está reservado en ese rango de fechas.")

        # Validar que el cliente no tenga una reserva activa o pendiente en ese periodo
        reservas_cliente = Reserva.objects.filter(
            cliente=cliente,
            estado__in=["pendiente", "confirmada"],
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio,
        ).exclude(id=self.instance.id if self.instance else None)

        if reservas_cliente.exists():
            raise serializers.ValidationError("El cliente ya tiene una reserva activa o pendiente en ese rango de fechas.")

        return data

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
        fecha_inicio = validated_data.get('fecha_inicio', instance.fecha_inicio)
        fecha_fin = validated_data.get('fecha_fin', instance.fecha_fin)
        vehiculo = validated_data.get('vehiculo', instance.vehiculo)

        dias = (fecha_fin - fecha_inicio).days
        monto_total = dias * vehiculo.precio_por_dia

        if monto_total <= 0:
            raise serializers.ValidationError("El monto total debe ser mayor a cero.")

        validated_data['monto_total'] = monto_total
        return super().update(instance, validated_data)


"""



#-------------------------MEJORA EN MODELOS-------------------------------#
#                                                                        #
#------------------------------------------------------------------------#

"""
class ModeloVehiculoSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
    tipo_nombre = serializers.CharField(source='tipo.descripcion', read_only=True)

    class Meta:
        model = ModeloVehiculo
        fields = ['id', 'nombre', 'marca', 'marca_nombre', 'tipo', 'tipo_nombre']
"""



# class ModeloVehiculoSerializer(serializers.ModelSerializer):
#     marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
#     tipo_nombre = serializers.CharField(source='tipo.descripcion', read_only=True)
#     es_premium = serializers.SerializerMethodField()
#
#     class Meta:
#         model = ModeloVehiculo
#         fields = ['id', 'nombre', 'marca', 'marca_nombre', 'tipo', 'tipo_nombre', 'es_premium']
#
#     def get_es_premium(self, obj):
#         return obj.es_premium()
#
#     def validate_nombre(self, value):
#
#         # que sea un nombre valido de por lo menos 2 caracteres (permitido A1, A3, etc.)
#         if len(value.strip()) < 2:
#             raise serializers.ValidationError("El nombre del modelo debe tener al menos 2 caracteres.")
#         return value
#
#     def validate(self, attrs):
#         marca = attrs.get('marca')
#         tipo = attrs.get('tipo')
#         nombre = attrs.get('nombre')
#
#         # Validar que el nombre del modelo no contenga la marca
#
#         if marca.nombre.lower() in nombre:
#             raise serializers.ValidationError("El nombre del modelo no debe contener el nombre de la marca.")
#
#         #  Validar que no puede repetirse nombre+marca+tipo
#         existe = ModeloVehiculo.objects.filter(
#             marca=marca,
#             nombre__iexact=nombre.strip(),
#             tipo=tipo
#         ).exclude(id=self.instance.id if self.instance else None)
#
#         if existe.exists():
#             raise serializers.ValidationError(
#                 "Ya existe un modelo con ese nombre para esa marca y tipo."
#             )
#
#         # Validación específica para marca genérica y tipo deportivo
#         if marca.nombre.lower() == 'genérica' and tipo.descripcion.lower() == 'deportivo':
#             raise serializers.ValidationError(
#                 "Los vehículos de marca genérica no pueden ser deportivos."
#             )
#
#         return attrs


class ModeloVehiculoSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
    tipo_nombre = serializers.CharField(source='tipo.descripcion', read_only=True)

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

        # Validar longitud mínima
        if len(nombre_normalizado) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres.")

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

        return attrs


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
            if qs.count() >= 5:
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


# #----------------------------USANDO MIXINS-------------------------------#
# #                                                                        #
# #------------------------------------------------------------------------#
#
#
# class AlquilerSerializer(RangoFechasVehiculoSerializerMixin):
#     cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
#     vehiculo_info = serializers.SerializerMethodField()
#     sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
#     monto_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
#
#     class Meta:
#         model = Alquiler
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
#             'estado',
#         ]
#
#     def get_vehiculo_info(self, obj):
#         return f"{obj.vehiculo.modelo.marca.nombre} {obj.vehiculo.modelo.nombre} - {obj.vehiculo.patente}"
#
#     def validate(self, data):
#         data = super().validate(data)
#         cliente = data.get('cliente')
#
#         conflictos_cliente = Alquiler.objects.filter(
#             cliente=cliente,
#             estado__in=["pendiente", "activo"],
#             fecha_inicio__lt=data['fecha_fin'],
#             fecha_fin__gt=data['fecha_inicio'],
#         ).exclude(id=self.instance.id if self.instance else None)
#
#         if conflictos_cliente.exists():
#             raise serializers.ValidationError("El cliente ya tiene un alquiler activo o pendiente en ese rango de fechas.")
#         return data
#
# class ReservaSerializer(RangoFechasVehiculoSerializerMixin):
#     cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
#     vehiculo_info = serializers.SerializerMethodField()
#     sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
#     monto_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
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
#             'estado',
#         ]
#
#     def get_vehiculo_info(self, obj):
#         return f"{obj.vehiculo.modelo.marca.nombre} {obj.vehiculo.modelo.nombre} - {obj.vehiculo.patente}"
#
#     def validate(self, data):
#         data = super().validate(data)
#         cliente = data.get('cliente')
#
#         conflictos_cliente = Reserva.objects.filter(
#             cliente=cliente,
#             estado__in=["pendiente", "confirmada"],
#             fecha_inicio__lt=data['fecha_fin'],
#             fecha_fin__gt=data['fecha_inicio'],
#         ).exclude(id=self.instance.id if self.instance else None)
#
#         if conflictos_cliente.exists():
#             raise serializers.ValidationError("El cliente ya tiene una reserva activa o pendiente en ese rango de fechas.")
#         return data
#
#
# #----------------------------USANDO MIXINS-------------------------------#
# #                                                                        #
# #------------------------------------------------------------------------#



# #----------------------------versión básica inicial----------------------#
# #                                                                        #
# #------------------------------------------------------------------------#
from decimal import Decimal


#############################esta reserva es la que estaba funcionando


# class ReservaSerializer(serializers.ModelSerializer):
#
#     cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
#     vehiculo_info = serializers.SerializerMethodField()
#     sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
#     #monto_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
#     monto_total = serializers.SerializerMethodField()
#     monto_usd = serializers.SerializerMethodField()
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
#
#     def get_vehiculo_info(self, obj):
#         return f"{obj.vehiculo.modelo.marca.nombre} {obj.vehiculo.modelo.nombre} - {obj.vehiculo.patente}"
#
# #----------------------------------------en caso de tener campos agregados antes-----------------------
#     def get_monto_total(self, obj):
#         # Si ya tiene un total distinto de cero, mostrarlo
#         if obj.monto_total and obj.monto_total > 0:
#             return obj.monto_total
#
#         # Si el monto es cero, lo calculamos
#         dias = (obj.fecha_fin - obj.fecha_inicio).days
#         if dias < 1:
#             dias = 1
#         return dias * obj.vehiculo.precio_por_dia
#
# # ---------------------------------------------------------------
#     def validate(self, data):
#         fecha_inicio = data.get('fecha_inicio')
#         fecha_fin = data.get('fecha_fin')
#         vehiculo = data.get('vehiculo')
#
#         # Validar que La fecha de inicio debe ser anterior a la fecha de fin
#         if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
#             raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")
#
#         # Validar que el vehículo no esté reservado o alquilado en ese rango de fechas
#         if vehiculo and fecha_inicio and fecha_fin:
#             reservas_conflictivas = Reserva.objects.filter(
#                 vehiculo=vehiculo,
#                 estado__in=['pendiente', 'confirmada'],
#                 fecha_inicio__lt=fecha_fin,
#                 fecha_fin__gt=fecha_inicio
#             ).exclude(id=self.instance.id if self.instance else None)
#
#             if reservas_conflictivas.exists():
#                 raise serializers.ValidationError("El vehículo ya tiene una reserva en ese rango de fechas.")
#
#             alquileres_conflictivos = Alquiler.objects.filter(
#                 vehiculo=vehiculo,
#                 estado__in=['pendiente', 'activo'],
#                 fecha_inicio__lt=fecha_fin,
#                 fecha_fin__gt=fecha_inicio
#             )
#
#             if alquileres_conflictivos.exists():
#                 raise serializers.ValidationError("El vehículo ya está alquilado en ese rango de fechas.")
#
#         return data
#
#     def calculate_monto_total(self, vehiculo, fecha_inicio, fecha_fin):
#         dias = (fecha_fin - fecha_inicio).days
#         if dias < 1:
#             dias = 1  # Por si hay error o alquiler por 1 día
#         return Decimal(dias) * vehiculo.precio_por_dia
#
#     def get_monto_usd(self, obj):
#         tipo_cambio = obtener_precio_dolar_blue()
#         if tipo_cambio and obj.monto_total:
#             return round(obj.monto_total / tipo_cambio, 2)
#         return "Valor del dólar no disponible"
#
#     def create(self, validated_data):
#         monto_total = self.calculate_monto_total(
#             validated_data['vehiculo'],
#             validated_data['fecha_inicio'],
#             validated_data['fecha_fin']
#         )
#         validated_data['monto_total'] = monto_total
#         return super().create(validated_data)
#
#     def update(self, instance, validated_data):
#         # Solo recalcular si se cambió alguna fecha o el vehículo
#         fecha_inicio = validated_data.get('fecha_inicio', instance.fecha_inicio)
#         fecha_fin = validated_data.get('fecha_fin', instance.fecha_fin)
#         vehiculo = validated_data.get('vehiculo', instance.vehiculo)
#
#         validated_data['monto_total'] = self.calculate_monto_total(vehiculo, fecha_inicio, fecha_fin)
#         return super().update(instance, validated_data)





#
#
# class AlquilerSerializer(serializers.ModelSerializer):
#     cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
#     vehiculo_info = serializers.SerializerMethodField()
#     sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
#     monto_total = serializers.SerializerMethodField()
#     monto_usd = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Alquiler
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
#
#     def get_vehiculo_info(self, obj):
#         return f"{obj.vehiculo.modelo.marca.nombre} {obj.vehiculo.modelo.nombre} - {obj.vehiculo.patente}"
#
#     def get_monto_total(self, obj):
#         # Si monto_total guardado es > 0, devuelve ese valor, si no lo calcula
#         if obj.monto_total and obj.monto_total > 0:
#             return obj.monto_total
#         else:
#             dias = (obj.fecha_fin - obj.fecha_inicio).days + 1
#             return dias * obj.vehiculo.precio_por_dia
#
#     def get_monto_usd(self, obj):
#         tipo_cambio = obtener_precio_dolar_blue()
#         if tipo_cambio and obj.monto_total:
#             return round(obj.monto_total / tipo_cambio, 2)
#         return "Valor del dólar no disponible"
#
#
#     def validate(self, data):
#         fecha_inicio = data['fecha_inicio']
#         fecha_fin = data['fecha_fin']
#         vehiculo = data['vehiculo']
#
#
#         # Validación: fecha de inicio < fecha de fin
#         if fecha_inicio >= fecha_fin:
#             raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")
#
#         # Validación: el vehículo no está alquilado en ese rango
#         alquileres_superpuestos = Alquiler.objects.filter(
#             vehiculo=vehiculo,
#             fecha_fin__gt=fecha_inicio,
#             fecha_inicio__lt=fecha_fin
#         )
#         if self.instance:
#             alquileres_superpuestos = alquileres_superpuestos.exclude(id=self.instance.id)
#
#         if alquileres_superpuestos.exists():
#             raise serializers.ValidationError("El vehículo ya está alquilado en esas fechas.")
#
#         # Validación: el vehículo no está reservado en ese rango
#         reservas_superpuestas = Reserva.objects.filter(
#             vehiculo=vehiculo,
#             estado__in=['pendiente', 'confirmada'],
#             fecha_fin__gt=fecha_inicio,
#             fecha_inicio__lt=fecha_fin
#         )
#
#         if reservas_superpuestas.exists():
#             raise serializers.ValidationError("El vehículo ya está reservado en esas fechas.")
#
#         return data
#
#
#     def create(self, validated_data):
#         dias = (validated_data['fecha_fin'] - validated_data['fecha_inicio']).days
#         dias = dias if dias > 0 else 1
#         precio_diario = validated_data['vehiculo'].precio_diario
#         validated_data['monto_total'] = dias * precio_diario
#         return super().create(validated_data)


class AlquilerSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
    vehiculo_info = serializers.SerializerMethodField()
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    monto_total = serializers.SerializerMethodField()
    monto_usd = serializers.SerializerMethodField()

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
        fecha_inicio = data['fecha_inicio']
        fecha_fin = data['fecha_fin']
        vehiculo = data['vehiculo']

        if fecha_inicio >= fecha_fin:
            raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")

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
            raise serializers.ValidationError("El vehículo ya está reservado en esas fechas.")

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


class ReservaSerializer(serializers.ModelSerializer):
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
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        vehiculo = data.get('vehiculo')

        if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
            raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")

        if vehiculo and fecha_inicio and fecha_fin:
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
        validated_data['monto_total'] = self.calculate_monto_total(vehiculo, fecha_inicio, fecha_fin)

        if 'sucursal' not in validated_data:
            validated_data['sucursal'] = vehiculo.sucursal

        return super().update(instance, validated_data)





# class AlquilerSerializer(serializers.ModelSerializer):
#     cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
#     vehiculo_info = serializers.SerializerMethodField()
#     sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
#     monto_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
#
#     class Meta:
#         model = Alquiler
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
#             'estado',
#         ]
#
#     def get_vehiculo_info(self, obj):
#         return f"{obj.vehiculo.modelo.marca.nombre} {obj.vehiculo.modelo.nombre} - {obj.vehiculo.patente}"
#
#     def validate(self, data):
#         fecha_inicio = data.get('fecha_inicio')
#         fecha_fin = data.get('fecha_fin')
#         vehiculo = data.get('vehiculo')
#
#         if fecha_inicio >= fecha_fin:
#             raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")
#
#         if vehiculo.estado not in ['disponible', 'reservado']:
#             raise serializers.ValidationError("El vehículo no se encuentra disponible para alquilar.")
#
#         # verificar conflictos con otros alquileres activos
#         conflictos = Alquiler.objects.filter(
#             vehiculo=vehiculo,
#             fecha_inicio__lt=fecha_fin,
#             fecha_fin__gt=fecha_inicio
#         ).exclude(id=self.instance.id if self.instance else None)
#
#         if conflictos.exists():
#             raise serializers.ValidationError("El vehículo ya está alquilado en ese rango de fechas.")
#
#         return data
#
#     def create(self, validated_data):
#         vehiculo = validated_data['vehiculo']
#         dias = (validated_data['fecha_fin'] - validated_data['fecha_inicio']).days
#         validated_data['monto_total'] = dias * vehiculo.precio_por_dia
#
#         # Cambiar estado del vehículo a "alquilado"
#         vehiculo.estado = 'alquilado'
#         vehiculo.save()
#
#         return super().create(validated_data)
#
#
# class ReservaSerializer(serializers.ModelSerializer):
#     cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
#     vehiculo_info = serializers.SerializerMethodField()
#     sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
#     monto_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
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
#             'estado',
#         ]
#
#     def get_vehiculo_info(self, obj):
#         return f"{obj.vehiculo.modelo.marca.nombre} {obj.vehiculo.modelo.nombre} - {obj.vehiculo.patente}"
#
#     def validate(self, data):
#         fecha_inicio = data.get('fecha_inicio')
#         fecha_fin = data.get('fecha_fin')
#         vehiculo = data.get('vehiculo')
#
#         if fecha_inicio >= fecha_fin:
#             raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")
#
#         if vehiculo.estado != 'disponible':
#             raise serializers.ValidationError("El vehículo no está disponible para reservar.")
#
#         # verificar reservas que se superpongan
#         conflictos = Reserva.objects.filter(
#             vehiculo=vehiculo,
#             fecha_inicio__lt=fecha_fin,
#             fecha_fin__gt=fecha_inicio
#         ).exclude(id=self.instance.id if self.instance else None)
#
#         if conflictos.exists():
#             raise serializers.ValidationError("El vehículo ya tiene una reserva en ese rango de fechas.")
#
#         return data
#
#     def create(self, validated_data):
#         vehiculo = validated_data['vehiculo']
#         dias = (validated_data['fecha_fin'] - validated_data['fecha_inicio']).days
#         validated_data['monto_total'] = dias * vehiculo.precio_por_dia
#
#         # Cambiar estado del vehículo a "reservado"
#         vehiculo.estado = 'reservado'
#         vehiculo.save()
#
#         return super().create(validated_data)