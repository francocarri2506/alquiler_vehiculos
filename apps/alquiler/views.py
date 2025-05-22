#
#
# import requests
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
#
# class ProvinciasListAPIView(APIView):
#     def get(self, request):
#         url = "https://apis.datos.gob.ar/georef/api/provincias"
#         response = requests.get(url)
#         if response.status_code == 200:
#             provincias = response.json().get("provincias", [])
#             return Response([p['nombre'] for p in provincias])
#         return Response({"error": "No se pudieron obtener las provincias"}, status=status.HTTP_502_BAD_GATEWAY)
#
# class DepartamentosListAPIView(APIView):
#     def get(self, request):
#         provincia = request.query_params.get("provincia")
#         if not provincia:
#             return Response({"error": "Debe especificar una provincia"}, status=status.HTTP_400_BAD_REQUEST)
#         url = f"https://apis.datos.gob.ar/georef/api/departamentos?provincia={provincia}&max=1000"
#         response = requests.get(url)
#         if response.status_code == 200:
#             departamentos = response.json().get("departamentos", [])
#             return Response([d['nombre'] for d in departamentos])
#         return Response({"error": "No se pudieron obtener los departamentos"}, status=status.HTTP_502_BAD_GATEWAY)
#
# class LocalidadesListAPIView(APIView):
#     def get(self, request):
#         provincia = request.query_params.get("provincia")
#         departamento = request.query_params.get("departamento")
#         if not provincia or not departamento:
#             return Response({"error": "Debe especificar provincia y departamento"}, status=status.HTTP_400_BAD_REQUEST)
#         url = f"https://apis.datos.gob.ar/georef/api/localidades?provincia={provincia}&departamento={departamento}&max=1000"
#         response = requests.get(url)
#         if response.status_code == 200:
#             localidades = response.json().get("localidades", [])
#             return Response([l['nombre'] for l in localidades])
#         return Response({"error": "No se pudieron obtener las localidades"}, status=status.HTTP_502_BAD_GATEWAY)



from django.shortcuts import render
import requests

def formulario_sucursal(request):
    # Obtener las provincias desde la API al cargar la página
    provincias_response = requests.get("https://apis.datos.gob.ar/georef/api/provincias")
    provincias = []
    if provincias_response.status_code == 200:
        provincias = provincias_response.json().get('provincias', [])

    return render(request, 'alquiler/formulario_sucursal.html', {'provincias': provincias})

