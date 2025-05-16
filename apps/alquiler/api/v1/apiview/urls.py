from django.urls import path


from .apiview import *

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
]