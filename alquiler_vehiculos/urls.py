
from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

#from apps.alquiler.api.v1.apiview import VehiculoListCreateAPIView, VehiculoRetrieveUpdateDestroyAPIView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
   # path('api/<str:version>/', include('apps.alquiler.api.urls')),
    path('api/v1/', include('apps.alquiler.api.v1.urls')), # Para APIView
    #path('api/v2/', include('apps.alquiler.api.v2.urls')),#copia exacta de v1 solo con viewset


    #apiview
   # path("vehiculos/", VehiculoListCreateAPIView.as_view(), name="vehiculo-list-create"),
   # path("vehiculos/<uuid:pk>/", VehiculoRetrieveUpdateDestroyAPIView.as_view(), name="vehiculo-detail"),

    #authenticacion
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),# para loguearce


    path('html/', include('apps.alquiler.urls_html')),  # Para vistas HTML tradicionales

    path('apiview/', include('apps.alquiler.api.v1.apiview.urls')),


    # Ruta para generar el esquema OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Documentación Swagger interactiva
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Documentación Redoc (estática y ordenada)
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),


]



