import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.alquiler.models import ModeloVehiculo


@pytest.mark.django_db
def test_creacion_modelo_exitosa(user_admin_con_token, marca_bmw, tipo_sedan):
    client = user_admin_con_token

    data = {
        "nombre": "Serie 3",
        "marca": str(marca_bmw.id),
        "tipo": str(tipo_sedan.id)
    }
    response = client.post("/api/v1/viewset/modelos/", data=data, format="json")


    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["nombre"] == "Serie 3"

#######################
#falla la creacion
#######################

@pytest.mark.django_db
def test_modelo_nombre_corto(user_admin_con_token, marca_bmw, tipo_sedan):
    client = user_admin_con_token

    data = {
        "nombre": "S",
        "marca": str(marca_bmw.id),
        "tipo": str(tipo_sedan.id)
    }

    response = client.post("/api/v1/viewset/modelos/", data=data, format="json")


    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "nombre" in response.data
    assert "al menos 2 caracteres" in response.data["nombre"][0]


@pytest.mark.django_db
def test_modelo_caracteres_invalidos(user_admin_con_token, marca_bmw, tipo_sedan):
    client = user_admin_con_token

    data = {
        "nombre": "Serie#5!",
        "marca": str(marca_bmw.id),
        "tipo": str(tipo_sedan.id)
    }

    response = client.post("/api/v1/viewset/modelos/", data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "caracteres especiales" in response.data["nombre"][0]

@pytest.mark.django_db
def test_modelo_nombre_contiene_marca(user_admin_con_token, marca_bmw, tipo_sedan):
    client = user_admin_con_token

    data = {
        "nombre": "BMW Serie 3",
        "marca": str(marca_bmw.id),
        "tipo": str(tipo_sedan.id)
    }

    response = client.post("/api/v1/viewset/modelos/", data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "no debe contener el nombre de la marca" in response.data["nombre"][0]

@pytest.mark.django_db
def test_modelo_duplicado(user_admin_con_token, marca_bmw, tipo_sedan):
    ModeloVehiculo.objects.create(nombre="Serie 1", marca=marca_bmw, tipo=tipo_sedan)

    client = user_admin_con_token
    data = {
        "nombre": "Serie 1",
        "marca": str(marca_bmw.id),
        "tipo": str(tipo_sedan.id)
    }

    response = client.post("/api/v1/viewset/modelos/", data=data, format="json")


    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Ya existe un modelo con ese nombre" in response.data["non_field_errors"][0]

@pytest.mark.django_db
def test_modelo_deportivo_con_marca_no_premium(user_admin_con_token, marca_fiat, tipo_deportivo):
    client = user_admin_con_token

    data = {
        "nombre": "Spider",
        "marca": str(marca_fiat.id),
        "tipo": str(tipo_deportivo.id)
    }

    response = client.post("/api/v1/viewset/modelos/", data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Solo las marcas Audi, BMW o Mercedes" in response.data["non_field_errors"][0]


@pytest.mark.django_db
def test_listar_modelos_detallado(user_admin_con_token, get_modelos):
    cliente = user_admin_con_token
    modelo1, modelo2 = get_modelos

    url = '/api/v1/viewset/modelos/'
    response = cliente.get(url)

    assert response.status_code == 200

    data = response.data['results']
    assert len(data) == 2

    # Asegurar que están los modelos esperados (independientemente del orden)
    nombres = [item['nombre'] for item in data]
    assert modelo1.nombre in nombres
    assert modelo2.nombre in nombres

    marcas = [item['marca_nombre'] for item in data]
    assert modelo1.marca.nombre in marcas
    assert modelo2.marca.nombre in marcas

    tipos = [item['tipo_nombre'] for item in data]
    assert modelo1.tipo.descripcion in tipos
    assert modelo2.tipo.descripcion in tipos



@pytest.mark.django_db
def test_listar_modelos_filtrados_por_marca(user_admin_con_token, get_modelos):
    cliente = user_admin_con_token
    modelo1, modelo2 = get_modelos

    assert modelo1.marca != modelo2.marca

    # Usamos el nombre de la marca porque así está definido el filtro
    response = cliente.get(f'/api/v1/viewset/modelos/?marca={modelo1.marca.nombre}')
    assert response.status_code == 200

    data = response.data['results']
    assert len(data) == 1
    assert data[0]['nombre'] == modelo1.nombre
    assert data[0]['marca_nombre'] == modelo1.marca.nombre


@pytest.mark.django_db
def test_listar_modelos_filtrados_por_tipo(user_admin_con_token, get_modelos):
    cliente = user_admin_con_token
    modelo1, modelo2 = get_modelos

    assert modelo1.tipo != modelo2.tipo

    # Usamos la descripción del tipo porque así está definido el filtro
    response = cliente.get(f'/api/v1/viewset/modelos/?tipo={modelo1.tipo.descripcion}')
    assert response.status_code == 200

    data = response.data['results']
    assert len(data) == 1
    assert data[0]['nombre'] == modelo1.nombre
    assert data[0]['tipo_nombre'] == modelo1.tipo.descripcion


@pytest.mark.django_db
def test_listar_modelos_usando_search(user_admin_con_token, get_modelos):
    cliente = user_admin_con_token
    modelo1, modelo2 = get_modelos

    # Buscamos por una parte del nombre del modelo1
    termino_busqueda = modelo1.nombre[:2].lower()  # Por ejemplo, "X5" -> "x"

    response = cliente.get(f'/api/v1/viewset/modelos/?search={termino_busqueda}')
    assert response.status_code == 200

    data = response.data['results']

    # Al menos un resultado debe coincidir
    assert any(modelo['id'] == str(modelo1.id) for modelo in data)

    # Verificamos que todos los resultados contengan el término en alguno de los campos buscables
    for modelo in data:
        contenido = (
            modelo['nombre'].lower() +
            modelo['marca_nombre'].lower() +
            modelo['tipo_nombre'].lower()
        )
        assert termino_busqueda in contenido

#############################
#probando test en action
############################

@pytest.mark.django_db
def test_asignar_tipo_exitosa(user_admin_con_token, get_modelos, get_tipos):
    cliente = user_admin_con_token
    modelo = get_modelos[0]
    nuevo_tipo = get_tipos[1]  #  get_tipos devuelve una lista de TipoVehiculo

    url = f'/api/v1/viewset/modelos/{modelo.id}/asignar_tipo/'
    data = {'tipo': str(nuevo_tipo.id)}

    response = cliente.post(url, data=data, format='json')


    assert response.status_code == status.HTTP_200_OK
    assert 'mensaje' in response.data

    modelo.refresh_from_db()
    assert modelo.tipo == nuevo_tipo