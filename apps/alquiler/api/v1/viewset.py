from rest_framework import viewsets, status
from apps.alquiler.models import Sucursal, Marca, TipoVehiculo, Vehiculo, Alquiler, Reserva
from .serializers import (
    SucursalSerializer, MarcaSerializer, TipoVehiculoSerializer,
    VehiculoSerializer, AlquilerSerializer, ReservaSerializer
)

from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime




class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer

class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer

class TipoVehiculoViewSet(viewsets.ModelViewSet):
    queryset = TipoVehiculo.objects.all()
    serializer_class = TipoVehiculoSerializer

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer



class AlquilerViewSet(viewsets.ModelViewSet):
    queryset = Alquiler.objects.all()
    serializer_class = AlquilerSerializer

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


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer


