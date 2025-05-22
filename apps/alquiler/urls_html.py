from django.urls import path
from . import views

urlpatterns = [
    path('nueva-sucursal/', views.formulario_sucursal, name='formulario_sucursal'),
]