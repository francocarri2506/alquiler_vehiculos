from django.contrib import admin
from .models import Sucursal, Marca, TipoVehiculo, Vehiculo, Alquiler, Reserva

@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'provincia', 'localidad', 'direccion')
    search_fields = ('nombre', 'provincia', 'localidad')

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)

@admin.register(TipoVehiculo)
class TipoVehiculoAdmin(admin.ModelAdmin):
    search_fields = ('descripcion',)

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'patente', 'estado', 'sucursal')
    list_filter = ('estado', 'sucursal', 'tipo')
    search_fields = ('modelo', 'patente')

@admin.register(Alquiler)
class AlquilerAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'vehiculo', 'fecha_inicio', 'fecha_fin', 'estado', 'sucursal')
    list_filter = ('estado',)
    search_fields = ('cliente__username', 'vehiculo__patente')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'vehiculo', 'fecha_inicio', 'fecha_fin', 'estado', 'sucursal')
    list_filter = ('estado',)
    search_fields = ('cliente__username', 'vehiculo__patente')