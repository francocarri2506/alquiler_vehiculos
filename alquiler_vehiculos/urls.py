"""
URL configuration for alquiler_vehiculos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

#from apps.alquiler.api.v1.apiview import VehiculoListCreateAPIView, VehiculoRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
   # path('api/<str:version>/', include('apps.alquiler.api.urls')),
    path('api/v1/', include('apps.alquiler.api.v1.urls')),
    #path('api/v2/', include('apps.alquiler.api.v2.urls')),#copia exacta de v1 solo con viewset


    #apiview
   # path("vehiculos/", VehiculoListCreateAPIView.as_view(), name="vehiculo-list-create"),
   # path("vehiculos/<uuid:pk>/", VehiculoRetrieveUpdateDestroyAPIView.as_view(), name="vehiculo-detail"),

]


