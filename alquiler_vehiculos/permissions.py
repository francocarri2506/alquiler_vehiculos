from rest_framework.permissions import DjangoModelPermissions

class StrictModelPermissions(DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

from rest_framework.permissions import BasePermission, SAFE_METHODS

class EsPropietarioOAdmin(BasePermission):
    """
    Permite acceso solo al propietario de la reserva o al admin.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.cliente == request.user
