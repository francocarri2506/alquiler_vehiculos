import pytest
from django.contrib.auth.models import Group, Permission

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


def create_user(username, documento_identidad, first_name='Nombre', last_name='Apellido', password='unpassword', email=None, *, is_active=True, is_staff=False):
    email = '{}@root.com'.format(username) if email is None else email #si no se pasa se crea solo

    # Primero buscamos si existe un usuario
    user = None
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        pass

    if user is None:
        # si no existe entonces creamos nuevo usuario
        user = User(
            username=username,
            email=email,
            dni=documento_identidad,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            is_staff=is_staff,
        )
        user.set_password(password) #para guardar el password hasheado
        user.save()

    return user

def crear_token_jwt(username, password):
    client = APIClient()
    response = client.post('/api/token/', {'username': username, 'password': password}, format='json')
    assert response.status_code == 200, f"No se pudo obtener token JWT para {username}"
    return response.data['access']

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_cliente_con_token():
    user = create_user('cliente', '11222333', is_staff=False, password='cliente123')

    # Grupo cliente con permisos de lectura
    grupo_cliente, _ = Group.objects.get_or_create(name='cliente')
    if grupo_cliente.permissions.count() == 0:
        permisos = Permission.objects.filter(
            codename__in=[
                'view_reserva',
                'add_reserva',
                'change_reserva',
                'delete_reserva',
                'view_sucursal',
            ]
        )
        grupo_cliente.permissions.set(permisos)

    user.groups.add(grupo_cliente) #agrego el usuario al grupo cliente
    user.save()

    token = crear_token_jwt('cliente', 'cliente123')
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    #return client
    return client, user #devuelvo el cliente autenticado y el usuario


@pytest.fixture
def user_admin_con_token():
    user = create_user('admin', '44555666', is_staff=True, password='admin123')

    grupo_admin, _ = Group.objects.get_or_create(name='admin')
    if grupo_admin.permissions.count() == 0:
        permisos = Permission.objects.all() # Asignar todos los permisos a admin
        grupo_admin.permissions.set(permisos)

    user.groups.add(grupo_admin)
    user.save()

    token = crear_token_jwt('admin', 'admin123')
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    return client



@pytest.fixture
def user_cliente2_con_token():
    # cliente diferente al dueño de la reserva(por ejemplo)
    user = create_user('intruso', '22334455', is_staff=False, password='intruso123')

    # Grupo cliente con permisos
    grupo_cliente, _ = Group.objects.get_or_create(name='cliente')
    if grupo_cliente.permissions.count() == 0:
        permisos = Permission.objects.filter(
            codename__in=[
                'view_reserva',
                'add_reserva',
                'change_reserva',
                'delete_reserva',
                'view_sucursal',
            ]
        )
        grupo_cliente.permissions.set(permisos)

    user.groups.add(grupo_cliente)
    user.save()

    token = crear_token_jwt('intruso', 'intruso123')
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    return client, user

