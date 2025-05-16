
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.alquiler.models import Sucursal, Marca, TipoVehiculo, Vehiculo, Alquiler, Reserva
from apps.alquiler.api.v1.serializers import (
    SucursalSerializer, MarcaSerializer, TipoVehiculoSerializer,
    VehiculoSerializer, AlquilerSerializer, ReservaSerializer
)

# ---------- Sucursal ----------
class SucursalListCreateAPIView(APIView):
    def get(self, request):
        sucursales = Sucursal.objects.all()
        serializer = SucursalSerializer(sucursales, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SucursalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SucursalRetrieveUpdateDeleteAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Sucursal, pk=pk)

    def get(self, request, pk):
        sucursal = self.get_object(pk)
        serializer = SucursalSerializer(sucursal)
        return Response(serializer.data)

    def put(self, request, pk):
        sucursal = self.get_object(pk)
        serializer = SucursalSerializer(sucursal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        sucursal = self.get_object(pk)
        sucursal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ---------- Marca ----------
class MarcaListCreateAPIView(APIView):
    def get(self, request):
        marcas = Marca.objects.all()
        serializer = MarcaSerializer(marcas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MarcaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MarcaRetrieveUpdateDeleteAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Marca, pk=pk)

    def get(self, request, pk):
        marca = self.get_object(pk)
        serializer = MarcaSerializer(marca)
        return Response(serializer.data)

    def put(self, request, pk):
        marca = self.get_object(pk)
        serializer = MarcaSerializer(marca, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        marca = self.get_object(pk)
        marca.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ---------- TipoVehiculo ----------
class TipoVehiculoListCreateAPIView(APIView):
    def get(self, request):
        tipos = TipoVehiculo.objects.all()
        serializer = TipoVehiculoSerializer(tipos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TipoVehiculoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TipoVehiculoRetrieveUpdateDeleteAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(TipoVehiculo, pk=pk)

    def get(self, request, pk):
        tipo = self.get_object(pk)
        serializer = TipoVehiculoSerializer(tipo)
        return Response(serializer.data)

    def put(self, request, pk):
        tipo = self.get_object(pk)
        serializer = TipoVehiculoSerializer(tipo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        tipo = self.get_object(pk)
        tipo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ---------- Vehiculo ----------
class VehiculoListCreateAPIView(APIView):
    def get(self, request):
        vehiculos = Vehiculo.objects.all()
        serializer = VehiculoSerializer(vehiculos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VehiculoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VehiculoRetrieveUpdateDeleteAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Vehiculo, pk=pk)

    def get(self, request, pk):
        vehiculo = self.get_object(pk)
        serializer = VehiculoSerializer(vehiculo)
        return Response(serializer.data)

    def put(self, request, pk):
        vehiculo = self.get_object(pk)
        serializer = VehiculoSerializer(vehiculo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        vehiculo = self.get_object(pk)
        vehiculo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ---------- Alquiler ----------
class AlquilerListCreateAPIView(APIView):
    def get(self, request):
        alquileres = Alquiler.objects.all()
        serializer = AlquilerSerializer(alquileres, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AlquilerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AlquilerRetrieveUpdateDeleteAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Alquiler, pk=pk)

    def get(self, request, pk):
        alquiler = self.get_object(pk)
        serializer = AlquilerSerializer(alquiler)
        return Response(serializer.data)

    def put(self, request, pk):
        alquiler = self.get_object(pk)
        serializer = AlquilerSerializer(alquiler, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        alquiler = self.get_object(pk)
        alquiler.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ---------- Reserva ----------
class ReservaListCreateAPIView(APIView):
    def get(self, request):
        reservas = Reserva.objects.all()
        serializer = ReservaSerializer(reservas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReservaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReservaRetrieveUpdateDeleteAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Reserva, pk=pk)

    def get(self, request, pk):
        reserva = self.get_object(pk)
        serializer = ReservaSerializer(reserva)
        return Response(serializer.data)

    def put(self, request, pk):
        reserva = self.get_object(pk)
        serializer = ReservaSerializer(reserva, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        reserva = self.get_object(pk)
        reserva.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
