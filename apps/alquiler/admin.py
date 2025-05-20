from django.contrib import admin
from .models import Sucursal, Marca, TipoVehiculo, Vehiculo, Alquiler, Reserva, ModeloVehiculo


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

"""
@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'patente', 'estado', 'sucursal')
    list_filter = ('estado', 'sucursal', 'tipo')
    search_fields = ('modelo', 'patente')
"""

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




#-------------------------MEJORA EN MODELOS-------------------------------#
#                                                                        #
#------------------------------------------------------------------------#

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'patente', 'estado', 'sucursal')
    list_filter = ('estado', 'sucursal', 'modelo__tipo')
    search_fields = ('modelo__nombre', 'patente')

    def marca(self, obj):
        return obj.modelo.marca.nombre
    marca.admin_order_field = 'modelo__marca__nombre'
    marca.short_description = 'Marca'


@admin.register(ModeloVehiculo)
class ModeloVehiculoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'marca', 'tipo', 'es_premium')  # Mostrar en la lista
    list_filter = ('marca', 'tipo', 'es_premium')             # Agregar filtros laterales
    search_fields = ('nombre', 'marca__nombre')               # Buscador
    readonly_fields = ('es_premium',)                         # Evitar edición manual