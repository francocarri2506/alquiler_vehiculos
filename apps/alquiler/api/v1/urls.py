from django.urls import path, include
from rest_framework.routers import DefaultRouter

# ViewSets
from apps.alquiler.api.v1.viewset import (
    SucursalViewSet, MarcaViewSet, TipoVehiculoViewSet,
    VehiculoViewSet, AlquilerViewSet, ReservaViewSet
)

# Router para ViewSet
router = DefaultRouter()
router.register(r'sucursales', SucursalViewSet)
router.register(r'marcas', MarcaViewSet)
router.register(r'tipos', TipoVehiculoViewSet)
router.register(r'vehiculos', VehiculoViewSet)
router.register(r'alquileres', AlquilerViewSet)
router.register(r'reservas', ReservaViewSet)

urlpatterns = [
    path('viewset/', include(router.urls)),            # → /api/v1/viewset/
    path('apiview/', include('apps.alquiler.api.v1.apiview.urls')),  # → /api/v1/apiview/
]