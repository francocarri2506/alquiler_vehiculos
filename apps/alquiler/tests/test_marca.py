import pytest
from rest_framework import status
from apps.alquiler.models import Marca


@pytest.fixture
def marca_existente(db):
    return Marca.objects.create(nombre="Toyota")


@pytest.mark.django_db
def test_creacion_marca_exitosa(user_admin_con_token):
    client = user_admin_con_token

    data = {"nombre": "Chevrolet"}
    response = client.post("/api/v1/viewset/marcas/", data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["nombre"] == "Chevrolet"


@pytest.mark.django_db
def test_actualizacion_marca_exitosa(user_admin_con_token, marca_existente):
    client = user_admin_con_token

    url = f"/api/v1/viewset/marcas/{marca_existente.id}/"
    data = {"nombre": "Nissan"}

    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["nombre"] == "Nissan"

@pytest.mark.django_db
def test_modificar_marca_falla_por_duplicado(user_admin_con_token):
    client = user_admin_con_token

    # Creamos dos marcas distintas
    marca1 = Marca.objects.create(nombre="Fiat")
    marca2 = Marca.objects.create(nombre="Honda")

    url = f"/api/v1/viewset/marcas/{marca2.id}/"
    data = {"nombre": "Fiat"}  # Intentamos ponerle el mismo nombre

    response = client.put(url, data=data, format="json")


    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "nombre" in response.data
    errores = response.data["nombre"]
    assert "Ya existe una marca con este nombre." in errores or "Ya existe marca con este nombre." in errores




@pytest.mark.django_db
@pytest.mark.parametrize("nombre, expected_msg", [
    ("", "Este campo no puede estar en blanco."),
    ("  ", "Este campo no puede estar en blanco."),
    ("a", "El nombre debe tener al menos 3 caracteres."),
    ("marca buena", "El nombre no puede contener la palabra 'marca'."),
    ("12345", "El nombre debe contener al menos una letra."),
    ("BMW!", "El nombre no debe contener caracteres especiales."),
    ("Toyota", "Ya existe marca con este nombre."),
    ("toyota", "Ya existe una marca con este nombre."),  # este está bien
])
def test_creacion_marca_errores(nombre, expected_msg, user_admin_con_token, marca_existente):
    client = user_admin_con_token

    data = {"nombre": nombre}
    response = client.post("/api/v1/viewset/marcas/", data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "nombre" in response.data

    errores = response.data["nombre"]

    if isinstance(errores, list):
        errores = [str(e) for e in errores]
        assert expected_msg in errores
    else:
        assert expected_msg in str(errores)

