from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from apps.alquiler.models import Sucursal, Marca, TipoVehiculo, Vehiculo, Alquiler, Reserva, HistorialEstadoAlquiler, \
    ModeloVehiculo
from .filters import ModeloVehiculoFilter
from .serializers import (
    SucursalSerializer, MarcaSerializer, TipoVehiculoSerializer,
    VehiculoSerializer, AlquilerSerializer, ReservaSerializer, HistorialEstadoAlquilerSerializer,
    ModeloVehiculoSerializer
)

from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter


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



class ModeloVehiculoViewSet(viewsets.ModelViewSet):
    queryset = ModeloVehiculo.objects.all()
    serializer_class = ModeloVehiculoSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ModeloVehiculoFilter
    ordering_fields = ['nombre', 'marca__nombre', 'tipo__nombre', 'es_premium']
    search_fields = ['nombre', 'marca__nombre', 'tipo__nombre']

    @action(detail=True, methods=['post'])
    def asignar_tipo(self, request, pk=None):
        """Permite cambiar el tipo de vehículo asociado a un modelo (operación extra al CRUD)."""
        modelo = self.get_object()
        nuevo_tipo_id = request.data.get('tipo_id')

        if not nuevo_tipo_id:
            return Response({'error': 'tipo_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        modelo.tipo_id = nuevo_tipo_id
        modelo.save()
        return Response({'mensaje': f'Tipo asignado correctamente a {modelo}'})

    @action(detail=False, methods=['get'])
    def por_marca(self, request):
        marca_id = request.query_params.get('marca_id')
        if marca_id:
            modelos = ModeloVehiculo.objects.filter(marca_id=marca_id)
        else:
            modelos = ModeloVehiculo.objects.none()
        serializer = self.get_serializer(modelos, many=True)
        return Response(serializer.data)



#-------------------------MEJORA EN MODELOS-------------------------------#
#                                                                        #
#------------------------------------------------------------------------#

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['estado', 'sucursal', 'modelo__marca', 'modelo__tipo']
    ordering_fields = ['año', 'precio_por_dia']
    search_fields = ['patente', 'modelo__nombre', 'modelo__marca__nombre']

    def get_queryset(self):
        queryset = super().get_queryset()
        sucursal_id = self.request.query_params.get('sucursal')
        if sucursal_id:
            queryset = queryset.filter(sucursal__id=sucursal_id)
        return queryset

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #
    #     # Filtro por sucursal si se pasa
    #     sucursal_id = self.request.query_params.get('sucursal')
    #     if sucursal_id:
    #         queryset = queryset.filter(sucursal__id=sucursal_id)
    #
    #     # Filtrar por estado 'disponible' solo si no se pasó explícitamente otro estado
    #     if 'estado' not in self.request.query_params:
    #         queryset = queryset.filter(estado='disponible')
    #
    #     return queryset


######## revisar estos 2 actions antes de presentar, me parece que la logica no es la correcta

    @action(detail=False, methods=['get'], url_path='disponibles_por_sucursal/(?P<sucursal_id>[0-9a-f-]+)')
    def disponibles_por_sucursal(self, request, sucursal_id=None):
        disponibles = Vehiculo.objects.filter(
            sucursal__id=sucursal_id,
            estado='disponible'
        )
        serializer = self.get_serializer(disponibles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], url_path='reservar')
    def reservar(self, request, pk=None):
        vehiculo = self.get_object()
        if vehiculo.estado != 'disponible':
            return Response(
                {"detalle": "El vehículo no está disponible para reservar."},
                status=status.HTTP_400_BAD_REQUEST
            )
        vehiculo.estado = 'reservado'
        vehiculo.save()
        return Response(
            {"detalle": "Vehículo reservado correctamente."},
            status=status.HTTP_200_OK
        )

# #DESCOMENTAR ESTO SI NO FUNCIONA
#
# class AlquilerViewSet(viewsets.ModelViewSet):
#     queryset = Alquiler.objects.all()
#     serializer_class = AlquilerSerializer
#
# # -------------------------FILTROS Y ORDEN--------------------------------#
# #                                                                         #
# # ------------------------------------------------------------------------#
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['estado', 'sucursal', 'cliente']
#     search_fields = ['cliente__username', 'vehiculo__patente']
#     ordering_fields = ['fecha_inicio', 'fecha_fin', 'monto_total']
#     ordering = ['fecha_inicio']
#
#     @action(detail=False, methods=['post'], url_path='calcular-monto')
#     def calcular_monto(self, request):
#         try:
#             fecha_inicio = datetime.strptime(request.data.get('fecha_inicio'), "%Y-%m-%d").date()
#             fecha_fin = datetime.strptime(request.data.get('fecha_fin'), "%Y-%m-%d").date()
#             vehiculo_id = request.data.get('vehiculo_id')
#
#             if fecha_fin < fecha_inicio:
#                 return Response({'error': 'La fecha de fin no puede ser anterior a la de inicio.'},
#                                 status=status.HTTP_400_BAD_REQUEST)
#
#             vehiculo = Vehiculo.objects.get(id=vehiculo_id)
#
#             # Verificar disponibilidad: no debe haber alquileres con estado pendiente o activo que se superpongan
#             existe_conflicto = Alquiler.objects.filter(
#                 vehiculo=vehiculo,
#                 estado__in=['pendiente', 'activo'],
#                 fecha_inicio__lte=fecha_fin,
#                 fecha_fin__gte=fecha_inicio
#             ).exists()
#
#             if existe_conflicto:
#                 return Response({'error': 'El vehículo no está disponible en el rango de fechas solicitado.'},
#                                 status=status.HTTP_409_CONFLICT)
#
#             dias = (fecha_fin - fecha_inicio).days + 1
#             monto_total = dias * vehiculo.precio_por_dia
#
#             return Response({'monto_total': monto_total}, status=status.HTTP_200_OK)
#
#         except Vehiculo.DoesNotExist:
#             return Response({'error': 'Vehículo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#
#     @action(detail=True, methods=['post'], url_path='cambiar-estado')
#     def cambiar_estado(self, request, pk=None):
#         alquiler = self.get_object()
#         estado_actual = alquiler.estado
#         nuevo_estado = request.data.get('estado')
#
#         ESTADOS_VALIDOS = ['pendiente', 'activo', 'finalizado', 'cancelado']
#
#         if nuevo_estado not in ESTADOS_VALIDOS:
#             return Response({'error': f'Estado no válido. Opciones: {ESTADOS_VALIDOS}'},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         if nuevo_estado == 'cancelado' and estado_actual != 'pendiente':
#             return Response({'error': 'Solo se puede cancelar un alquiler pendiente.'},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         if nuevo_estado == 'finalizado' and estado_actual != 'activo':
#             return Response({'error': 'Solo se puede finalizar un alquiler activo.'},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         if estado_actual in ['finalizado', 'cancelado']:
#             return Response({'error': f'No se puede modificar un alquiler que ya está {estado_actual}.'},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         # Guardar historial
#         HistorialEstadoAlquiler.objects.create(
#             alquiler=alquiler,
#             estado_anterior=estado_actual,
#             estado_nuevo=nuevo_estado,
#             cambiado_por=request.user if request.user.is_authenticated else None
#         )
#
#         alquiler.estado = nuevo_estado
#         alquiler.save()
#         return Response({'mensaje': f'Estado actualizado a {nuevo_estado}'}, status=status.HTTP_200_OK)
#
#
# class ReservaViewSet(viewsets.ModelViewSet):
#     queryset = Reserva.objects.all()
#     serializer_class = ReservaSerializer
#
#
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['estado', 'cliente', 'vehiculo']
#     #filterset_fields = ['estado', 'sucursal', 'cliente']
#     search_fields = ['cliente__username', 'vehiculo__patente']
#     ordering_fields = ['fecha_inicio', 'fecha_fin']
#     ordering = ['fecha_inicio']


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


"""
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


# #----------------------------versión básica inicial----------------------#
# #                                                                        #
# #------------------------------------------------------------------------#


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        reserva = self.get_object()

        if reserva.estado != 'pendiente':
            return Response({'error': 'Solo se pueden confirmar reservas pendientes.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Crear alquiler
        alquiler = Alquiler.objects.create(
            cliente=reserva.cliente,
            vehiculo=reserva.vehiculo,
            sucursal=reserva.sucursal,
            fecha_inicio=reserva.fecha_inicio,
            fecha_fin=reserva.fecha_fin,
            monto_total=reserva.monto_total,  # Esto se puede recalcular luego si es necesario
            estado='activo'
        )

        # Cambiar estado de la reserva
        reserva.estado = 'confirmada'
        reserva.save()

        alquiler_serializado = AlquilerSerializer(alquiler)

        return Response({
            'mensaje': 'Reserva confirmada y alquiler creado.',
            'alquiler': alquiler_serializado.data
        }, status=status.HTTP_201_CREATED)


class AlquilerViewSet(viewsets.ModelViewSet):
    queryset = Alquiler.objects.all()
    serializer_class = AlquilerSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['estado', 'vehiculo', 'cliente']
    search_fields = ['vehiculo__patente', 'cliente__username']
    ordering_fields = ['fecha_inicio', 'fecha_fin', 'monto_total']

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['post'], url_path='calcular-monto')
    def calcular_monto(self, request):
        try:
            fecha_inicio = datetime.strptime(request.data.get('fecha_inicio'), "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(request.data.get('fecha_fin'), "%Y-%m-%d").date()
            vehiculo_id = request.data.get('vehiculo_id')

            if fecha_fin < fecha_inicio:
                return Response({'error': 'La fecha de fin no puede ser anterior a la de inicio.'},
                                status=status.HTTP_400_BAD_REQUEST)

            dias = (fecha_fin - fecha_inicio).days + 1
            vehiculo = Vehiculo.objects.get(id=vehiculo_id)
            monto_total = dias * vehiculo.precio_por_dia

            return Response({'monto_total': monto_total}, status=status.HTTP_200_OK)

        except Vehiculo.DoesNotExist:
            return Response({'error': 'Vehículo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        alquiler = self.get_object()
        estado_actual = alquiler.estado
        nuevo_estado = request.data.get('estado')

        ESTADOS_VALIDOS = ['pendiente', 'activo', 'finalizado', 'cancelado']

        if nuevo_estado not in ESTADOS_VALIDOS:
            return Response({'error': f'Estado no válido. Opciones: {ESTADOS_VALIDOS}'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validaciones específicas por transición
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


# class ReservaViewSet(viewsets.ModelViewSet):
#     queryset = Reserva.objects.all()
#     serializer_class = ReservaSerializer
#
#     # Filtros
#     filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
#     filterset_fields = ['vehiculo', 'cliente', 'sucursal', 'estado']
#     search_fields = ['vehiculo__marca', 'vehiculo__modelo', 'cliente__nombre', 'cliente__apellido']
#     ordering_fields = ['fecha_inicio', 'fecha_fin', 'monto_total']
#     ordering = ['fecha_inicio']  # orden predeterminado
#
#     # Acción personalizada: Confirmar reserva
#     @action(detail=True, methods=['post'], url_path='confirmar')
#     def confirmar_reserva(self, request, pk=None):
#         reserva = self.get_object()
#
#         if reserva.estado != 'pendiente':
#             return Response({'error': 'Solo se pueden confirmar reservas pendientes.'},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         # Crear el alquiler basado en la reserva
#         alquiler = Alquiler.objects.create(
#             cliente=reserva.cliente,
#             vehiculo=reserva.vehiculo,
#             sucursal=reserva.sucursal,
#             fecha_inicio=reserva.fecha_inicio,
#             fecha_fin=reserva.fecha_fin,
#             monto_total=reserva.monto_total,
#             estado='activo'
#         )
#
#         # Actualizar estado de la reserva y vehículo
#         reserva.estado = 'confirmada'
#         reserva.save()
#         vehiculo = reserva.vehiculo
#         vehiculo.estado = 'alquilado'
#         vehiculo.save()
#
#         return Response({
#             'mensaje': 'Reserva confirmada y alquiler generado exitosamente.',
#             'alquiler_id': alquiler.id
#         }, status=status.HTTP_201_CREATED)
#
#     # Acción personalizada: Cancelar reserva
#     @action(detail=True, methods=['post'], url_path='cancelar')
#     def cancelar_reserva(self, request, pk=None):
#         reserva = self.get_object()
#
#         if reserva.estado != 'pendiente':
#             return Response({'error': 'Solo se pueden cancelar reservas pendientes.'},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         reserva.estado = 'cancelada'
#         reserva.save()
#
#         # Cambiar vehículo a disponible si no tiene otras reservas pendientes
#         vehiculo = reserva.vehiculo
#         if not Reserva.objects.filter(vehiculo=vehiculo, estado='pendiente').exists():
#             vehiculo.estado = 'disponible'
#             vehiculo.save()
#
#         return Response({'mensaje': 'Reserva cancelada correctamente.'}, status=status.HTTP_200_OK)
#
# class AlquilerViewSet(viewsets.ModelViewSet):
#     queryset = Alquiler.objects.all()
#     serializer_class = AlquilerSerializer
#
#     filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
#     filterset_fields = ['vehiculo', 'cliente', 'sucursal', 'estado']
#     search_fields = ['vehiculo__marca', 'vehiculo__modelo', 'cliente__nombre', 'cliente__apellido']
#     ordering_fields = ['fecha_inicio', 'fecha_fin', 'monto_total']
#     ordering = ['fecha_inicio']