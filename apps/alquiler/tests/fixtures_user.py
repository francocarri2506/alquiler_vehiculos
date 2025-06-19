
import pytest
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

# def create_user(username, documento_identidad, first_name='Nombre', last_name='Apellido', password='unpassword', email=None, *, is_active=True, is_staff=False):
#     email = '{}@root.com'.format(username) if email is None else email
#
#     user, created = User.objects.get_or_create(
#         username=username,
#         email=email,
#         documento_identidad=documento_identidad
#     )
#
#     if created:
#         user.first_name = first_name
#         user.last_name = last_name
#         user.is_active = is_active
#         user.is_staff = is_staff
#         user.set_password(password)
#         user.save()
#
#     return user

def create_user(username, documento_identidad, first_name='Nombre', last_name='Apellido', password='unpassword', email=None, *, is_active=True, is_staff=False):
    email = '{}@root.com'.format(username) if email is None else email

    # Primero buscamos usuario por username y dni (campo único)
    user = None
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        pass

    if user is None:
        # Creamos nuevo usuario, esta vez asignando dni desde el principio
        user = User(
            username=username,
            email=email,
            dni=documento_identidad,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            is_staff=is_staff,
        )
        user.set_password(password)
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
                'delete_reserva'
            ]
        )
        grupo_cliente.permissions.set(permisos)

    user.groups.add(grupo_cliente)
    user.save()

    token = crear_token_jwt('cliente', 'cliente123')
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    #return client
    return client, user


@pytest.fixture
def user_admin_con_token():
    user = create_user('admin', '44555666', is_staff=True, password='admin123')

    grupo_admin, _ = Group.objects.get_or_create(name='admin')
    if grupo_admin.permissions.count() == 0:
        permisos = Permission.objects.all()
        grupo_admin.permissions.set(permisos)

    user.groups.add(grupo_admin)
    user.save()

    token = crear_token_jwt('admin', 'admin123')
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    return client



@pytest.fixture
def user_cliente_con_token_intruso():
    # Crear otro usuario distinto
    user = create_user('intruso', '22334455', is_staff=False, password='intruso123')

    # Grupo cliente con permisos
    grupo_cliente, _ = Group.objects.get_or_create(name='cliente')
    if grupo_cliente.permissions.count() == 0:
        permisos = Permission.objects.filter(
            codename__in=[
                'view_reserva',
                'add_reserva',
                'change_reserva',
                'delete_reserva'
            ]
        )
        grupo_cliente.permissions.set(permisos)

    user.groups.add(grupo_cliente)
    user.save()

    token = crear_token_jwt('intruso', 'intruso123')
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    return client, user


"""
@pytest.fixture
def user_admin_con_permisos(db):
    # Crear o conseguir grupo admin
    admin_group, created = Group.objects.get_or_create(name='admin')
    if created or admin_group.permissions.count() == 0:
        # Asignar todos los permisos a admin
        permisos = Permission.objects.all()
        admin_group.permissions.set(permisos)
        admin_group.save()

    # Crear o conseguir grupo cliente
    #cliente_group, _ = Group.objects.get_or_create(name='cliente')
    # Ejemplo: asignar permisos limitados a cliente
    # permisos_cliente = Permission.objects.filter(codename__in=['view_sucursal'])
    # cliente_group.permissions.set(permisos_cliente)
    # cliente_group.save()

    # Crear usuario
    user = User.objects.create_user(
        username='admin',
        password='admin123',
        email='admin@correo.com',
        is_staff=True,
    )
    # Asignar grupo admin al usuario
    user.groups.add(admin_group)
    user.save()

    # Cliente API
    client = APIClient()
    # Obtener token JWT vía endpoint (ajustar ruta si es distinta)
    response = client.post('/api/token/', {'username': 'admin', 'password': 'admin123'}, format='json')
    assert response.status_code == 200, "No se pudo obtener token JWT"

    access_token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    return client


@pytest.fixture
def user_autenticado(db):
    user = User.objects.create_user(
        username='admin',
        password='admin123',
        email='admin@correo.com',
        is_staff=True
    )

    # Obtener el permiso add_sucursal
    app_label = 'alquiler'  # cambia por el nombre real de tu app si es distinto
    model_name = 'sucursal'
    permiso = Permission.objects.get(codename=f'add_{model_name}', content_type__app_label=app_label)
    user.user_permissions.add(permiso)

    client = APIClient()
    # Obtener token JWT via endpoint, por ejemplo:
    response = client.post('/api/token/', {'username': 'admin', 'password': 'admin123'}, format='json')
    access_token = response.data['access']

    client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    return client

@pytest.fixture
def user_cliente_sin_permisos(db):
    # Crear grupo cliente con permisos limitados (solo lectura, opcional)
    cliente_group, _ = Group.objects.get_or_create(name='cliente')
    if cliente_group.permissions.count() == 0:
        permisos_lectura = Permission.objects.filter(codename__startswith='view_')
        cliente_group.permissions.set(permisos_lectura)
        cliente_group.save()

    user = User.objects.create_user(
        username='cliente',
        password='cliente123',
        email='cliente@correo.com',
        is_staff=False
    )
    user.groups.add(cliente_group)
    user.save()

    client = APIClient()
    response = client.post('/api/token/', {'username': 'cliente', 'password': 'cliente123'}, format='json')
    assert response.status_code == 200, "No se pudo obtener token JWT (cliente)"
    access_token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    return client

"""