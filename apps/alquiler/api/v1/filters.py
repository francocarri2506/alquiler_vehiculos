
import django_filters

from apps.alquiler.models import ModeloVehiculo


class ModeloVehiculoFilter(django_filters.FilterSet):
    marca = django_filters.CharFilter(field_name='marca__nombre', lookup_expr='icontains')
    tipo = django_filters.CharFilter(field_name='tipo__descripcion', lookup_expr='icontains')
    es_premium = django_filters.BooleanFilter()

    class Meta:
        model = ModeloVehiculo
        fields = ['marca', 'tipo']