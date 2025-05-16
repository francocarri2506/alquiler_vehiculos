from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('username', 'email', 'dni', 'telefono', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'dni')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('dni', 'telefono', 'direccion'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('dni', 'telefono', 'direccion'),
        }),
    )