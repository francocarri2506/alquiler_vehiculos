from django.urls import path, include
from rest_framework.routers import DefaultRouter

# ViewSets
from apps.alquiler.api.v1.viewset import (
    SucursalViewSet, MarcaViewSet, TipoVehiculoViewSet,
    VehiculoViewSet, AlquilerViewSet, ReservaViewSet, HistorialEstadoAlquilerViewSet, ModeloVehiculoViewSet
)
#from apps.alquiler.views import ProvinciasListAPIView, DepartamentosListAPIView, LocalidadesListAPIView

# Router para ViewSet
router = DefaultRouter()
router.register(r'sucursales', SucursalViewSet)
router.register(r'marcas', MarcaViewSet)
router.register(r'tipos', TipoVehiculoViewSet)
router.register(r'modelos', ModeloVehiculoViewSet)
router.register(r'vehiculos', VehiculoViewSet)
#router.register(r'alquileres', AlquilerViewSet)
router.register(r'alquileres', AlquilerViewSet, basename='alquiler')
router.register(r'reservas', ReservaViewSet)
router.register(r'historial-alquileres', HistorialEstadoAlquilerViewSet, basename='historial-alquiler')



urlpatterns = [
    path('viewset/', include(router.urls)),            #  /api/v1/viewset/
    path('apiview/', include('apps.alquiler.api.v1.apiview.urls')),  #  /api/v1/apiview/

    #path('provincias/', ProvinciasListAPIView.as_view(), name='provincias'),
    #path('departamentos/', DepartamentosListAPIView.as_view(), name='departamentos'),
    #path('localidades/', LocalidadesListAPIView.as_view(), name='localidades'),

]


