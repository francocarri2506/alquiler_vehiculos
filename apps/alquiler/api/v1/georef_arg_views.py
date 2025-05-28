import requests
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

GEORREF_BASE = "https://apis.datos.gob.ar/georef/api"

class ProvinciasAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            response = requests.get(f"{GEORREF_BASE}/provincias?campos=nombre&max=100")
            data = response.json()
            return Response(data.get("provincias", []))
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DepartamentosAPIView(APIView):

    permission_classes = [AllowAny]
    def get(self, request):
        provincia = request.query_params.get("provincia")
        if not provincia:
            return Response({"error": "Falta el parámetro 'provincia'."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            response = requests.get(f"{GEORREF_BASE}/departamentos", params={"provincia": provincia, "campos": "nombre", "max": 1000})
            data = response.json()
            return Response(data.get("departamentos", []))
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LocalidadesAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        provincia = request.query_params.get("provincia")
        departamento = request.query_params.get("departamento")
        if not provincia or not departamento:
            return Response({"error": "Faltan los parámetros 'provincia' y/o 'departamento'."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            response = requests.get(f"{GEORREF_BASE}/localidades", params={"provincia": provincia, "departamento": departamento, "campos": "nombre", "max": 1000})
            data = response.json()
            return Response(data.get("localidades", []))
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)