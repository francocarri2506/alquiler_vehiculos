from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.alquiler.api.v2.viewset import SucursalViewSet, MarcaViewSet, TipoVehiculoViewSet, VehiculoViewSet, \
    AlquilerViewSet, ReservaViewSet

router = DefaultRouter()
router.register(r'sucursales', SucursalViewSet)
router.register(r'marcas', MarcaViewSet)
router.register(r'tipos', TipoVehiculoViewSet)
router.register(r'vehiculos', VehiculoViewSet)
router.register(r'alquileres', AlquilerViewSet)
router.register(r'reservas', ReservaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
