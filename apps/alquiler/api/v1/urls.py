from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.alquiler.api.v1.georef_arg_views import ProvinciasAPIView, DepartamentosAPIView, LocalidadesAPIView
# ViewSets
from apps.alquiler.api.v1.viewset import (
    SucursalViewSet, MarcaViewSet, TipoVehiculoViewSet,
    VehiculoViewSet, AlquilerViewSet, ReservaViewSet, HistorialEstadoAlquilerViewSet, ModeloVehiculoViewSet
)
#from apps.alquiler.views import ProvinciasListAPIView, DepartamentosListAPIView, LocalidadesListAPIView



# inicializar el Router DRF para ViewSet una sola vez
router = DefaultRouter()

#Registrar un viewset

router.register(r'sucursales', SucursalViewSet)
router.register(r'marcas', MarcaViewSet)
router.register(r'tipos', TipoVehiculoViewSet)
router.register(r'modelos', ModeloVehiculoViewSet)
router.register(r'vehiculos', VehiculoViewSet)
router.register(r'alquileres', AlquilerViewSet, basename='alquiler')
router.register(r'reservas', ReservaViewSet)
router.register(r'historial-alquileres', HistorialEstadoAlquilerViewSet, basename='historial-alquiler')




urlpatterns = [
    path('viewset/', include(router.urls)),            #  /api/v1/viewset/
    path('apiview/', include('apps.alquiler.api.v1.apiview.urls')),  #  /api/v1/apiview/

    #path('georef/', include('georef.urls')),

    #path('provincias/', ProvinciasAPIView.as_view(), name='provincias'),
    #path('departamentos/', DepartamentosAPIView.as_view(), name='departamentos'),
    #path('localidades/', LocalidadesAPIView.as_view(), name='localidades'),

]


