from datetime import date

from rest_framework import serializers

from apps.alquiler.models import Sucursal, Marca, TipoVehiculo, Vehiculo, Alquiler, Reserva, HistorialEstadoAlquiler


class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = '__all__'

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'

class TipoVehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoVehiculo
        fields = '__all__'
"""
class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = '__all__'
"""
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


