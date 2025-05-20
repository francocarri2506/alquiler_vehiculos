from rest_framework import serializers
from datetime import date

# class RangoFechasVehiculoSerializerMixin(serializers.ModelSerializer):
#     """
#     Mixin para validaciones comunes entre reservas y alquileres.
#     """
#
#     def validate(self, data):
#         fecha_inicio = data.get('fecha_inicio')
#         fecha_fin = data.get('fecha_fin')
#         vehiculo = data.get('vehiculo')
#
#         if fecha_inicio < date.today():
#             raise serializers.ValidationError("La fecha de inicio no puede ser anterior a hoy.")
#
#         if fecha_fin <= fecha_inicio:
#             raise serializers.ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")
#
#         # Validación de disponibilidad del vehículo
#         model_class = self.Meta.model
#         instancia_id = self.instance.id if self.instance else None
#
#         conflictos = model_class.objects.filter(
#             vehiculo=vehiculo,
#             fecha_inicio__lt=fecha_fin,
#             fecha_fin__gt=fecha_inicio,
#         ).exclude(id=instancia_id)
#
#         if conflictos.exists():
#             raise serializers.ValidationError("El vehículo ya está reservado o alquilado en ese rango de fechas.")
#
#         return data
#
#     def calcular_monto_total(self, vehiculo, fecha_inicio, fecha_fin):
#         dias = (fecha_fin - fecha_inicio).days
#         monto_total = dias * vehiculo.precio_por_dia
#         if monto_total <= 0:
#             raise serializers.ValidationError("El monto total debe ser mayor a cero.")
#         return monto_total
#
#     def create(self, validated_data):
#         validated_data['monto_total'] = self.calcular_monto_total(
#             validated_data['vehiculo'],
#             validated_data['fecha_inicio'],
#             validated_data['fecha_fin']
#         )
#         return super().create(validated_data)
#
#     def update(self, instance, validated_data):
#         vehiculo = validated_data.get('vehiculo', instance.vehiculo)
#         fecha_inicio = validated_data.get('fecha_inicio', instance.fecha_inicio)
#         fecha_fin = validated_data.get('fecha_fin', instance.fecha_fin)
#
#         validated_data['monto_total'] = self.calcular_monto_total(vehiculo, fecha_inicio, fecha_fin)
#         return super().update(instance, validated_data)
#

from rest_framework import serializers
from datetime import date

from apps.alquiler.models import Alquiler, Reserva


class RangoFechasVehiculoSerializerMixin(serializers.ModelSerializer):
    """
    Mixin para validaciones comunes entre reservas y alquileres.
    """

    def validate(self, data):
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        vehiculo = data.get('vehiculo')

        if fecha_inicio < date.today():
            raise serializers.ValidationError("La fecha de inicio no puede ser anterior a hoy.")

        if fecha_fin <= fecha_inicio:
            raise serializers.ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")

        if vehiculo.estado in ['mantenimiento']:
            raise serializers.ValidationError("El vehículo está en mantenimiento y no se puede usar.")

        model_class = self.Meta.model
        instancia_id = self.instance.id if self.instance else None

        # Evitar conflictos con otras reservas/alquileres confirmados/activos
        conflictos = model_class.objects.filter(
            vehiculo=vehiculo,
            estado__in=["pendiente", "confirmada", "activo"],  # según modelo
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio,
        ).exclude(id=instancia_id)

        if conflictos.exists():
            raise serializers.ValidationError("El vehículo ya está reservado o alquilado en ese rango de fechas.")

        return data

    def calcular_monto_total(self, vehiculo, fecha_inicio, fecha_fin):
        dias = (fecha_fin - fecha_inicio).days
        monto_total = dias * vehiculo.precio_por_dia
        if monto_total <= 0:
            raise serializers.ValidationError("El monto total debe ser mayor a cero.")
        return monto_total

    def create(self, validated_data):
        validated_data['monto_total'] = self.calcular_monto_total(
            validated_data['vehiculo'],
            validated_data['fecha_inicio'],
            validated_data['fecha_fin']
        )

        instancia = super().create(validated_data)

        # Cambiar estado del vehículo si corresponde
        self.actualizar_estado_vehiculo(instancia)

        return instancia

    def update(self, instance, validated_data):
        vehiculo = validated_data.get('vehiculo', instance.vehiculo)
        fecha_inicio = validated_data.get('fecha_inicio', instance.fecha_inicio)
        fecha_fin = validated_data.get('fecha_fin', instance.fecha_fin)

        validated_data['monto_total'] = self.calcular_monto_total(vehiculo, fecha_inicio, fecha_fin)

        instancia = super().update(instance, validated_data)

        # Actualizar estado del vehículo si corresponde
        self.actualizar_estado_vehiculo(instancia)

        return instancia

    def actualizar_estado_vehiculo(self, instancia):
        """
        Cambia el estado del vehículo según el modelo.
        """
        if hasattr(instancia, 'vehiculo'):
            if isinstance(instancia, Alquiler):
                if instancia.estado == 'pendiente':
                    instancia.vehiculo.estado = 'alquilado'
                    instancia.vehiculo.save()
            elif isinstance(instancia, Reserva):
                if instancia.estado == 'confirmada':
                    instancia.vehiculo.estado = 'reservado'
                    instancia.vehiculo.save()