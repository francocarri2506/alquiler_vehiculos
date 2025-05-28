from django.urls import path, include

from .apiview import *
from ..georef_arg_views import ProvinciasAPIView, DepartamentosAPIView, LocalidadesAPIView




urlpatterns = [
    path('sucursales/', SucursalListCreateAPIView.as_view()),
    path('sucursales/<int:pk>/', SucursalRetrieveUpdateDeleteAPIView.as_view()),

    path('marcas/', MarcaListCreateAPIView.as_view()),
    path('marcas/<int:pk>/', MarcaRetrieveUpdateDeleteAPIView.as_view()),

    path('tipos-vehiculo/', TipoVehiculoListCreateAPIView.as_view()),
    path('tipos-vehiculo/<int:pk>/', TipoVehiculoRetrieveUpdateDeleteAPIView.as_view()),

    path('vehiculos/', VehiculoListCreateAPIView.as_view()),
    path('vehiculos/<int:pk>/', VehiculoRetrieveUpdateDeleteAPIView.as_view()),

    path('alquileres/', AlquilerListCreateAPIView.as_view()),
    path('alquileres/<int:pk>/', AlquilerRetrieveUpdateDeleteAPIView.as_view()),

    path('reservas/', ReservaListCreateAPIView.as_view()),
    path('reservas/<int:pk>/', ReservaRetrieveUpdateDeleteAPIView.as_view()),

    path('alquileres/calcular-monto/', CalcularMontoAPIView.as_view(), name='calcular-monto'),


    #para mostrar directamamente de la api externa
    path('provincias/', ProvinciasAPIView.as_view(), name='provincias'),
    # http://127.0.0.1:8000/api/v1/apiview/provincias/

    path('departamentos/', DepartamentosAPIView.as_view(), name='departamentos'),
    #http://127.0.0.1:8000/api/v1/apiview/departamentos/?provincia=Catamarca
    path('localidades/', LocalidadesAPIView.as_view(), name='localidades'),
    #http://127.0.0.1:8000/api/v1/apiview/localidades/?provincia=Catamarca&departamento=Santa María




]