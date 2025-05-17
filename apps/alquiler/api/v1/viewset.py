from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from apps.alquiler.models import Sucursal, Marca, TipoVehiculo, Vehiculo, Alquiler, Reserva, HistorialEstadoAlquiler
from .serializers import (
    SucursalSerializer, MarcaSerializer, TipoVehiculoSerializer,
    VehiculoSerializer, AlquilerSerializer, ReservaSerializer, HistorialEstadoAlquilerSerializer
)

from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime




class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer

    #filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nombre', 'provincia','departamento','localidad']
    search_fields = ['nombre', 'direccion']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nombre']
    search_fields = ['nombre']
    ordering_fields = ['nombre']
    ordering = ['nombre']

class TipoVehiculoViewSet(viewsets.ModelViewSet):
    queryset = TipoVehiculo.objects.all()
    serializer_class = TipoVehiculoSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['descripcion']
    search_fields = ['descripcion']
    ordering_fields = ['descripcion']
    ordering = ['descripcion']

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['marca', 'modelo']
    search_fields = ['modelo', 'patente']
    ordering_fields = ['modelo', 'patente']
    ordering = ['modelo']

class AlquilerViewSet(viewsets.ModelViewSet):
    queryset = Alquiler.objects.all()
    serializer_class = AlquilerSerializer

# -------------------------FILTROS Y ORDEN--------------------------------#
#                                                                         #
# ------------------------------------------------------------------------#
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'sucursal', 'cliente']
    search_fields = ['cliente__username', 'vehiculo__patente']
    ordering_fields = ['fecha_inicio', 'fecha_fin', 'monto_total']
    ordering = ['fecha_inicio']

    """

    @action(detail=False, methods=['post'], url_path='calcular-monto')
    def calcular_monto(self, request):
        try:
            fecha_inicio = datetime.strptime(request.data.get('fecha_inicio'), "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(request.data.get('fecha_fin'), "%Y-%m-%d").date()
            vehiculo_id = request.data.get('vehiculo_id')

            if fecha_fin < fecha_inicio:
                return Response({'error': 'La fecha de fin no puede ser anterior a la de inicio.'}, status=status.HTTP_400_BAD_REQUEST)

            dias = (fecha_fin - fecha_inicio).days + 1  # Incluye el día de inicio
            vehiculo = Vehiculo.objects.get(id=vehiculo_id)
            monto_total = dias * vehiculo.precio_por_dia

            return Response({'monto_total': monto_total}, status=status.HTTP_200_OK)

        except Vehiculo.DoesNotExist:
            return Response({'error': 'Vehículo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    """


    @action(detail=False, methods=['post'], url_path='calcular-monto')
    def calcular_monto(self, request):
        try:
            fecha_inicio = datetime.strptime(request.data.get('fecha_inicio'), "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(request.data.get('fecha_fin'), "%Y-%m-%d").date()
            vehiculo_id = request.data.get('vehiculo_id')

            if fecha_fin < fecha_inicio:
                return Response({'error': 'La fecha de fin no puede ser anterior a la de inicio.'},
                                status=status.HTTP_400_BAD_REQUEST)

            vehiculo = Vehiculo.objects.get(id=vehiculo_id)

            # Verificar disponibilidad: no debe haber alquileres con estado pendiente o activo que se superpongan
            existe_conflicto = Alquiler.objects.filter(
                vehiculo=vehiculo,
                estado__in=['pendiente', 'activo'],
                fecha_inicio__lte=fecha_fin,
                fecha_fin__gte=fecha_inicio
            ).exists()

            if existe_conflicto:
                return Response({'error': 'El vehículo no está disponible en el rango de fechas solicitado.'},
                                status=status.HTTP_409_CONFLICT)

            dias = (fecha_fin - fecha_inicio).days + 1
            monto_total = dias * vehiculo.precio_por_dia

            return Response({'monto_total': monto_total}, status=status.HTTP_200_OK)

        except Vehiculo.DoesNotExist:
            return Response({'error': 'Vehículo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    """
    @action(detail=True, methods=['post'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        alquiler = self.get_object()
        estado_actual = alquiler.estado
        nuevo_estado = request.data.get('estado')

        ESTADOS_VALIDOS = ['pendiente', 'activo', 'finalizado', 'cancelado']

        if nuevo_estado not in ESTADOS_VALIDOS:
            return Response({'error': f'Estado no válido. Opciones: {ESTADOS_VALIDOS}'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Reglas de transición de estado
        if nuevo_estado == 'cancelado' and estado_actual != 'pendiente':
            return Response({'error': 'Solo se puede cancelar un alquiler pendiente.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if nuevo_estado == 'finalizado' and estado_actual != 'activo':
            return Response({'error': 'Solo se puede finalizar un alquiler activo.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if estado_actual in ['finalizado', 'cancelado']:
            return Response({'error': f'No se puede modificar un alquiler que ya está {estado_actual}.'},
                            status=status.HTTP_400_BAD_REQUEST)

        alquiler.estado = nuevo_estado
        alquiler.save()
        return Response({'mensaje': f'Estado actualizado a {nuevo_estado}'}, status=status.HTTP_200_OK)
    """

    @action(detail=True, methods=['post'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        alquiler = self.get_object()
        estado_actual = alquiler.estado
        nuevo_estado = request.data.get('estado')

        ESTADOS_VALIDOS = ['pendiente', 'activo', 'finalizado', 'cancelado']

        if nuevo_estado not in ESTADOS_VALIDOS:
            return Response({'error': f'Estado no válido. Opciones: {ESTADOS_VALIDOS}'},
                            status=status.HTTP_400_BAD_REQUEST)

        if nuevo_estado == 'cancelado' and estado_actual != 'pendiente':
            return Response({'error': 'Solo se puede cancelar un alquiler pendiente.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if nuevo_estado == 'finalizado' and estado_actual != 'activo':
            return Response({'error': 'Solo se puede finalizar un alquiler activo.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if estado_actual in ['finalizado', 'cancelado']:
            return Response({'error': f'No se puede modificar un alquiler que ya está {estado_actual}.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Guardar historial
        HistorialEstadoAlquiler.objects.create(
            alquiler=alquiler,
            estado_anterior=estado_actual,
            estado_nuevo=nuevo_estado,
            cambiado_por=request.user if request.user.is_authenticated else None
        )

        alquiler.estado = nuevo_estado
        alquiler.save()
        return Response({'mensaje': f'Estado actualizado a {nuevo_estado}'}, status=status.HTTP_200_OK)


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer


    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'cliente', 'vehiculo']
    #filterset_fields = ['estado', 'sucursal', 'cliente']
    search_fields = ['cliente__username', 'vehiculo__patente']
    ordering_fields = ['fecha_inicio', 'fecha_fin']
    ordering = ['fecha_inicio']


class HistorialEstadoAlquilerViewSet(viewsets.ReadOnlyModelViewSet): #ReadOnlyModelViewSet solo permite GET (listar y recuperar)
    queryset = HistorialEstadoAlquiler.objects.select_related('alquiler', 'cambiado_por').all()
    serializer_class = HistorialEstadoAlquilerSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]

    # Filtros exactos
    filterset_fields = ['alquiler', 'estado_anterior', 'estado_nuevo', 'cambiado_por']

    # Campos permitidos para ordenamiento
    ordering_fields = ['fecha_cambio', 'estado_anterior', 'estado_nuevo']
    ordering = ['-fecha_cambio']  # por defecto

    # Campos para búsqueda general (parcial)
    search_fields = [
        'alquiler__id',              # búsqueda por ID de alquiler
        'cambiado_por__username',    # búsqueda por nombre de usuario
    ]