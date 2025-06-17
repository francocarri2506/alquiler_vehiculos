import pytest
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient
from apps.alquiler.models import Sucursal

@pytest.mark.django_db
def test_creacion_sucursal_exitosa(user_autenticado, datos_geograficos):
    provincia, departamento, localidad = datos_geograficos
    client = user_autenticado


    data = {
        "nombre": "Sucursal Centro",
        "provincia": provincia.nombre,
        "departamento": departamento.nombre,
        "localidad": localidad.nombre,
        "direccion": "Av. Colón 1234"
    }

    #response = client.post('/api/sucursales/', data, format='json')
    response = client.post('/api/v1/viewset/sucursales/', data, format='json')

    print("STATUS:", response.status_code)
    print("DATA:", response.data)  # Aquí mostramos detalle del error

    assert response.status_code == 201
    assert Sucursal.objects.filter(nombre="Sucursal Centro").exists()


@pytest.mark.django_db
def test_cliente_no_puede_crear_sucursal(user_cliente_sin_permisos, datos_geograficos):
    provincia, departamento, localidad = datos_geograficos
    client = user_cliente_sin_permisos

    data = {
        "nombre": "Sucursal Cliente",
        "provincia": provincia.nombre,
        "departamento": departamento.nombre,
        "localidad": localidad.nombre,
        "direccion": "Av. Siempre Viva 123"
    }

    response = client.post('/api/v1/viewset/sucursales/', data, format='json')
    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_puede_crear_sucursal(user_admin_con_permisos, datos_geograficos):
    provincia, departamento, localidad = datos_geograficos
    client = user_admin_con_permisos

    data = {
        "nombre": "Sucursal Admin",
        "provincia": provincia.nombre,
        "departamento": departamento.nombre,
        "localidad": localidad.nombre,
        "direccion": "Av. Colón 1234"
    }

    response = client.post('/api/v1/viewset/sucursales/', data, format='json')

    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == 201



@pytest.mark.django_db
#def test_listado_sucursales(user_cliente_sin_permisos, crear_sucursales_existentes):
    #client = user_cliente_sin_permisos
def test_listado_sucursales(user_cliente_con_token, crear_sucursales_existentes):

    client = user_cliente_con_token
    response = client.get('/api/v1/viewset/sucursales/')

    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == 200
    assert response.data['count'] == 4

    nombres = [sucursal['nombre'] for sucursal in response.data['results']]
    assert "Auto Rentas" in nombres
    assert "CarrosSeguros" in nombres
    assert "Renta y Ve" in nombres



@pytest.mark.django_db
def test_crear_sucursal_duplicada(user_admin_con_token, crear_sucursales_existentes):
    client = user_admin_con_token
    sucursal_existente = crear_sucursales_existentes[0]

    data = {
        "nombre": sucursal_existente.nombre,
        "direccion": sucursal_existente.direccion,
        "provincia": sucursal_existente.provincia.nombre,
        "departamento": sucursal_existente.departamento.nombre,
        "localidad": sucursal_existente.localidad.nombre
    }

    response = client.post('/api/v1/viewset/sucursales/', data=data, format='json')

    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Ya existe una sucursal con el mismo nombre y ubicación geográfica.' in str(response.data)


@pytest.mark.django_db
def test_modificar_sucursal_exitosa(user_admin_con_token, crear_sucursales_existentes):
    client = user_admin_con_token
    sucursal = crear_sucursales_existentes[0]

    url = f'/api/v1/viewset/sucursales/{sucursal.id}/'
    nuevo_dato = {
        "nombre": "Sucursal Modificada",
        "direccion": sucursal.direccion,
        "provincia": sucursal.provincia.nombre,
        "departamento": sucursal.departamento.nombre,
        "localidad": sucursal.localidad.nombre
    }

    response = client.put(url, data=nuevo_dato, format='json')

    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["nombre"] == "Sucursal Modificada"





@pytest.mark.django_db
def test_modificar_sucursal_falla_por_duplicado(user_admin_con_token, crear_sucursales_existentes):
    client = user_admin_con_token
    sucursal_1 = crear_sucursales_existentes[0]
    sucursal_2 = crear_sucursales_existentes[1]

    url = f'/api/v1/viewset/sucursales/{sucursal_2.id}/'
    datos_duplicados = {
        "nombre": sucursal_1.nombre,
        "direccion": sucursal_1.direccion,
        "provincia": sucursal_1.provincia.nombre,
        "departamento": sucursal_1.departamento.nombre,
        "localidad": sucursal_1.localidad.nombre
    }

    response = client.put(url, data=datos_duplicados, format='json')

    assert response.status_code == 400
    assert '__all__' in response.data
    assert 'Ya existe una sucursal con el mismo nombre y ubicación geográfica.' in response.data['__all__']


@pytest.mark.django_db
def test_modificar_sucursal_falla_por_departamento_no_perteneciente(user_admin_con_token, crear_sucursales_existentes):
    client = user_admin_con_token
    sucursal = crear_sucursales_existentes[0]

    from apps.alquiler.models import Departamento

    departamentos_no_validos = Departamento.objects.exclude(provincia=sucursal.provincia)
    if not departamentos_no_validos.exists():
        pytest.skip("No hay departamentos fuera de la provincia para testear")

    departamento_no_valido = departamentos_no_validos.first()

    url = f'/api/v1/viewset/sucursales/{sucursal.id}/'
    nuevo_dato = {
        "nombre": sucursal.nombre,
        "direccion": sucursal.direccion,
        "provincia": sucursal.provincia.nombre,
        "departamento": departamento_no_valido.nombre,
        "localidad": sucursal.localidad.nombre,
    }

    response = client.put(url, data=nuevo_dato, format='json')
    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mensaje = str(response.data).lower()
    assert "departamento" in mensaje
    assert "no existe en la provincia" in mensaje

@pytest.mark.django_db
def test_modificar_sucursal_falla_por_duplicado(user_admin_con_token, crear_sucursales_existentes):
    client = user_admin_con_token

    sucursal1 = crear_sucursales_existentes[0]
    sucursal2 = crear_sucursales_existentes[1]

    url = f'/api/v1/viewset/sucursales/{sucursal1.id}/'

    datos_duplicados = {
        "nombre": sucursal2.nombre,
        "direccion": sucursal2.direccion,
        "provincia": sucursal2.provincia.nombre,
        "departamento": sucursal2.departamento.nombre,
        "localidad": sucursal2.localidad.nombre,
    }

    response = client.put(url, data=datos_duplicados, format='json')

    print(response.status_code)
    print(response.data)

    assert response.status_code == 400
    assert 'non_field_errors' in response.data
    assert 'Ya existe una sucursal con el mismo nombre' in response.data['non_field_errors'][0]




@pytest.mark.django_db
@pytest.mark.parametrize("data, expected_field, expected_msg", [
    # Campos vacíos
    (
        {
            "nombre": "",
            "direccion": "Av. Siempre Viva",
            "provincia": "Catamarca",
            "departamento": "Santa María",
            "localidad": "Santa María"
        },
        "nombre",
        "Este campo no puede estar en blanco."
    ),
    (
        {
            "nombre": "Sucursal Nueva",
            "direccion": "",
            "provincia": "Catamarca",
            "departamento": "Santa María",
            "localidad": "Santa María"
        },
        "direccion",
        "Este campo no puede estar en blanco."
    ),
    # Provincia inexistente
    (
        {
            "nombre": "Sucursal Nueva",
            "direccion": "Av. Siempre Viva",
            "provincia": "Provincia Fantasma",
            "departamento": "Santa María",
            "localidad": "Santa María"
        },
        "non_field_errors",
        "La provincia 'Provincia Fantasma' no existe en la base de datos."
    ),
    # Departamento inválido dentro de provincia válida
    (
        {
            "nombre": "Sucursal Nueva",
            "direccion": "Av. Siempre Viva",
            "provincia": "Catamarca",
            "departamento": "Otro Departamento",
            "localidad": "Santa María"
        },
        "non_field_errors",
        "El departamento 'Otro Departamento' no existe en la provincia 'Catamarca'."
    ),
    # Localidad inválida dentro de departamento válido
    (
        {
            "nombre": "Sucursal Nueva",
            "direccion": "Av. Siempre Viva",
            "provincia": "Catamarca",
            "departamento": "Santa María",
            "localidad": "Otra Localidad"
        },
        "non_field_errors",
        "La localidad 'Otra Localidad' no existe en el departamento 'Santa María'."
    ),
])
def test_creacion_sucursal_errores_mensajes(
    user_admin_con_token,
    provincia_catamarca,
    departamento_santa_maria,
    localidad_santa_maria,
    data,
    expected_field,
    expected_msg
):
    client = user_admin_con_token
    response = client.post('/api/v1/viewset/sucursales/', data=data, format='json')

    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert expected_field in response.data

    errors = response.data[expected_field]

    if isinstance(errors, list):
        # Convertimos los ErrorDetail a str si hace falta
        errores_normalizados = [str(err) for err in errors]
        assert expected_msg in errores_normalizados
    else:
        assert expected_msg in str(errors)