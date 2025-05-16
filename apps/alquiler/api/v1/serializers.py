from rest_framework import serializers

from apps.alquiler.models import Sucursal, Marca, TipoVehiculo, Vehiculo, Alquiler, Reserva


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

class AlquilerSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
    vehiculo_info = serializers.SerializerMethodField()
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)

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
        ]

    def get_vehiculo_info(self, obj):
        return f"{obj.vehiculo.marca.nombre} {obj.vehiculo.modelo} - {obj.vehiculo.patente}"


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