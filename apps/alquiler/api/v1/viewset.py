import uuid

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework.permissions import DjangoModelPermissions

from apps.alquiler.models import Sucursal, Marca, TipoVehiculo, Vehiculo, Alquiler, Reserva, HistorialEstadoAlquiler, \
    ModeloVehiculo
from .filters import ModeloVehiculoFilter
from .serializers import (
    SucursalSerializer, MarcaSerializer, TipoVehiculoSerializer,
    VehiculoSerializer, AlquilerSerializer, ReservaSerializer, HistorialEstadoAlquilerSerializer,
    ModeloVehiculoSerializer, SucursalCreateSerializer
)

from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

import requests

from django.utils.timezone import now
from datetime import datetime, date
#-------------------------------------------------------------------------#
#                             SUCURSAL                                    #
#-------------------------------------------------------------------------#

# class SucursalViewSet(viewsets.ModelViewSet):
#     queryset = Sucursal.objects.all()
#     serializer_class = SucursalSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['nombre', 'provincia', 'departamento', 'localidad']
#     search_fields = ['nombre', 'direccion']
#     ordering_fields = ['nombre']
#     ordering = ['nombre']
#
#

class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nombre', 'provincia', 'departamento', 'localidad']
    search_fields = ['nombre', 'direccion']
    ordering_fields = ['nombre']
    ordering = ['nombre']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SucursalCreateSerializer
        return SucursalSerializer



#-------------------------------------------------------------------------#
#                                 MARCA                                   #
#-------------------------------------------------------------------------#
class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nombre']
    search_fields = ['nombre']
    ordering_fields = ['nombre']
    ordering = ['nombre']



#-------------------------------------------------------------------------#
#                                 TIPO                                    #
#-------------------------------------------------------------------------#
class TipoVehiculoViewSet(viewsets.ModelViewSet):
    queryset = TipoVehiculo.objects.all()
    serializer_class = TipoVehiculoSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['descripcion']
    search_fields = ['descripcion']
    ordering_fields = ['descripcion']
    ordering = ['descripcion']



#-------------------------------------------------------------------------#
#                                MODELO                                   #
#-------------------------------------------------------------------------#
class ModeloVehiculoViewSet(viewsets.ModelViewSet):
    queryset = ModeloVehiculo.objects.all()
    serializer_class = ModeloVehiculoSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ModeloVehiculoFilter
    ordering_fields = ['nombre', 'marca__nombre', 'tipo__descripcion', 'es_premium']
    search_fields = ['nombre', 'marca__nombre', 'tipo__descripcion']



    @action(detail=True, methods=['post'])
    def asignar_tipo(self, request, pk=None):
        """   especie de patch
        Permite cambiar el tipo de vehículo asociado a un modelo.
        Espera un campo 'tipo_id' en el body con el UUID del nuevo tipo.
        """
        modelo = self.get_object()
        nuevo_tipo_id =  request.data.get('tipo')

        if not nuevo_tipo_id:
            return Response({'error': 'tipo es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            nuevo_tipo = TipoVehiculo.objects.get(id=nuevo_tipo_id)
        except TipoVehiculo.DoesNotExist:
            raise NotFound('El tipo de vehículo con ese ID no existe.')

        modelo.tipo = nuevo_tipo
        modelo.save()

        return Response({'mensaje': f'Tipo asignado correctamente a {modelo}'})

    @action(detail=False, methods=['get'])
    def por_marca(self, request):
        """
        Devuelve los modelos de una marca si el UUID es válido y existe.
        """
        marca_id = request.query_params.get('marca_id')

        if not marca_id:
            return Response({'error': 'Se requiere el parámetro marca_id'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar que sea un UUID válido
        try:
            uuid_obj = uuid.UUID(marca_id)
        except ValueError:
            raise ValidationError("El valor proporcionado no es un UUID válido.")

        # Verificar que exista la marca
        try:
            Marca.objects.get(id=uuid_obj)
        except Marca.DoesNotExist:
            raise NotFound("La marca con ese ID no existe.")

        modelos = ModeloVehiculo.objects.filter(marca_id=uuid_obj)
        serializer = self.get_serializer(modelos, many=True)
        return Response(serializer.data)


#-------------------------------------------------------------------------#
#                                VEHICULO                                 #
#-------------------------------------------------------------------------#

######################################################probando los permisos:###############

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    permission_classes = [DjangoModelPermissions]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['estado', 'sucursal', 'modelo__marca', 'modelo__tipo']
    ordering_fields = ['año', 'precio_por_dia']
    search_fields = ['patente', 'modelo__nombre', 'modelo__marca__nombre']

    def get_queryset(self):
        user = self.request.user

        # Si es admin (tiene permisos de cambio sobre vehiculo), ve todos los vehiculos
        if user.has_perm('vehiculos.change_vehiculo'):
            return Vehiculo.objects.all().order_by('id')

        # Si es cliente, filtra solo vehículos disponibles
        disponibles = Vehiculo.objects.filter(estado='disponible').order_by('id')

        # Excluir vehículos con alquiler activo
        alquileres_activos = Alquiler.objects.filter(estado='activo').values_list('vehiculo_id', flat=True)
        disponibles = disponibles.exclude(id__in=alquileres_activos)

        # Excluir vehículos con reservas confirmadas o pendientes vigentes
        hoy = now().date()
        reservas_vigentes = Reserva.objects.filter(
            estado__in=['pendiente', 'confirmada'],
            fecha_fin__gte=hoy
        ).values_list('vehiculo_id', flat=True)
        disponibles = disponibles.exclude(id__in=reservas_vigentes)

        # Opcional: permitir filtrar por sucursal desde el cliente también
        sucursal_id = self.request.query_params.get('sucursal')
        if sucursal_id:
            disponibles = disponibles.filter(sucursal__id=sucursal_id)

        return disponibles


    @action(detail=False, methods=['get'], url_path=r'disponibles_por_sucursal/(?P<sucursal_id>[0-9a-f-]+)')
    def disponibles_por_sucursal(self, request, sucursal_id=None): #disponibles en sucursal x, excluyendo alquilados y reservados
        # Mismo criterio de disponibilidad para cliente
        hoy = now().date()
        alquileres_activos = Alquiler.objects.filter(estado='activo').values_list('vehiculo_id', flat=True)

        reservas_vigentes = Reserva.objects.filter(
            estado__in=['pendiente', 'confirmada'],
            fecha_fin__gte=hoy
        ).values_list('vehiculo_id', flat=True)

        disponibles = Vehiculo.objects.filter(
            sucursal__id=sucursal_id,
            estado='disponible'
        ).exclude(
            id__in=alquileres_activos
        ).exclude(
            id__in=reservas_vigentes
        )

        serializer = self.get_serializer(disponibles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='reservar')
    def reservar(self, request, pk=None): #Endpoint para reservar un vehículo si está disponible
        vehiculo = self.get_object()

        # Verificamos que esté disponible
        if vehiculo.estado != 'disponible':
            return Response(
                {"detalle": "El vehículo no está disponible para reservar."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificamos que no tenga un alquiler activo
        if Alquiler.objects.filter(vehiculo=vehiculo, estado='activo').exists(): #Que no esté alquilado (Alquiler.estado = activo)
            return Response(
                {"detalle": "El vehículo ya está alquilado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificamos que no tenga una reserva vigente
        hoy = now().date()
        if Reserva.objects.filter(
            vehiculo=vehiculo,
            estado__in=['pendiente', 'confirmada'],
            fecha_fin__gte=hoy
        ).exists():
            return Response(
                {"detalle": "El vehículo ya tiene una reserva vigente."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # si esta todo bien se cambia el estado del vehiculo
        vehiculo.estado = 'reservado'
        vehiculo.save()
        return Response(
            {"detalle": "Vehículo reservado correctamente."},
            status=status.HTTP_200_OK
        )



#-------------------------------------------------------------------------#
#                                RESERVA                                  #
#-------------------------------------------------------------------------#

from rest_framework.permissions import IsAuthenticated

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'sucursal', 'cliente']
    search_fields = ['cliente__username', 'vehiculo__patente']
    ordering_fields = ['fecha_inicio', 'fecha_fin', 'monto_total']
    ordering = ['fecha_inicio']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Reserva.objects.all()
        return Reserva.objects.filter(cliente=user)  #  solo puede ver sus reservas

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff:
            cliente = serializer.validated_data.get('cliente')
            if not cliente:
                raise PermissionDenied("Debes indicar el cliente al crear una reserva como administrador.")
            serializer.save()
        else:
            # Cliente no puede pasar otro cliente
            serializer.save(cliente=user)

    def perform_update(self, serializer):
        user = self.request.user
        reserva = self.get_object()
        if user.is_staff:
            serializer.save()
        else:
            if reserva.cliente != user:
                raise PermissionDenied("No tienes permiso para modificar esta reserva.")
            serializer.save(cliente=user)  # fuerza que siga siendo él

    def perform_destroy(self, instance):
        if self.request.user.is_staff or instance.cliente == self.request.user:
            instance.delete()
        else:
            raise PermissionDenied("No tienes permiso para eliminar esta reserva.")

    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        reserva = self.get_object()

        if reserva.estado != 'pendiente':
            return Response({'error': 'Solo se pueden confirmar reservas pendientes.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Crear el alquiler basado en la reserva

        alquiler = Alquiler.objects.create(
            cliente=reserva.cliente,
            vehiculo=reserva.vehiculo,
            sucursal=reserva.sucursal,
            fecha_inicio=reserva.fecha_inicio,
            fecha_fin=reserva.fecha_fin,
            monto_total=reserva.monto_total,
            estado='activo'
        )

        reserva.estado = 'confirmada'
        reserva.save()

        alquiler_serializado = AlquilerSerializer(alquiler)
        return Response({
            'mensaje': 'Reserva confirmada y alquiler creado.',
            'alquiler': alquiler_serializado.data
        }, status=status.HTTP_201_CREATED)

# Acción personalizada: Cancelar reserva
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


#-------------------------------------------------------------------------#
#                                ALQUILER                                 #
#-------------------------------------------------------------------------#

class AlquilerViewSet(viewsets.ModelViewSet):
    queryset = Alquiler.objects.all()
    serializer_class = AlquilerSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['estado', 'vehiculo', 'cliente']
    search_fields = ['vehiculo__patente', 'cliente__username']
    ordering_fields = ['fecha_inicio', 'fecha_fin', 'monto_total']
    ordering = ['fecha_inicio']

    def get_queryset(self):
        user = self.request.user
        # Si es superusuario o tiene permiso especial, puede ver todo
        if user.is_superuser or user.has_perm('alquiler.view_all_alquiler'):
            return Alquiler.objects.all()
        # Si no, solo los alquileres del cliente logueado
        return Alquiler.objects.filter(cliente=user)

    def perform_create(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'mensaje': 'Alquiler eliminado correctamente.'}, status=status.HTTP_200_OK)

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


    @action(detail=True, methods=['get', 'post'], url_path='tiempo-restante')
    def tiempo_restante(self, request, pk=None):
        alquiler = self.get_object()

        if request.method == 'GET':
            hoy = date.today()
            if alquiler.fecha_fin < hoy:
                return Response({'mensaje': 'El alquiler ya finalizó.'})
            dias_restantes = (alquiler.fecha_fin - hoy).days
            return Response({'dias_restantes': dias_restantes})

        elif request.method == 'POST':
            # Solo el cliente puede extender su alquiler
            if request.user != alquiler.cliente:
                return Response({'error': 'No tiene permiso para modificar este alquiler.'}, status=403)

            nueva_fecha_fin = request.data.get('fecha_fin')

            try:
                nueva_fecha_fin = datetime.strptime(nueva_fecha_fin, "%Y-%m-%d").date()
            except ValueError:
                return Response({'error': 'Formato de fecha incorrecto. Use YYYY-MM-DD.'}, status=400)

            if nueva_fecha_fin <= alquiler.fecha_fin:
                return Response({'error': 'La nueva fecha debe ser posterior a la fecha de fin actual.'}, status=400)

            alquiler.fecha_fin = nueva_fecha_fin
            alquiler.save()
            return Response({'mensaje': f'Fecha de fin extendida a {nueva_fecha_fin}.'}, status=200)




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




#-------------------------------------------------------------------------#
#                             HISTORIAL-ESTADO                            #
#-------------------------------------------------------------------------#
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
