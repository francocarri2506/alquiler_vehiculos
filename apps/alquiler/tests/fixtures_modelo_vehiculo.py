import pytest
from apps.alquiler.models import Marca, TipoVehiculo, ModeloVehiculo


@pytest.fixture
def marca_bmw():
    return Marca.objects.create(nombre="BMW")

@pytest.fixture
def marca_fiat():
    return Marca.objects.create(nombre="Fiat")

@pytest.fixture
def tipo_sedan():
    return TipoVehiculo.objects.create(descripcion="Sedan")

@pytest.fixture
def tipo_deportivo():
    return TipoVehiculo.objects.create(descripcion="Deportivo")

@pytest.fixture
def modelo_existente(db, marca_bmw, tipo_deportivo):
    # Modelo existente para pruebas de unicidad
    return ModeloVehiculo.objects.create(
        nombre="M3",
        marca=marca_bmw,
        tipo=tipo_deportivo
    )


@pytest.fixture
def modelo_bmw_x5(marca_bmw, tipo_deportivo):
    return ModeloVehiculo.objects.create(nombre='X5', marca=marca_bmw, tipo=tipo_deportivo)

@pytest.fixture
def modelo_ford_focus(marca_ford, tipo_sedan):
    return ModeloVehiculo.objects.create(nombre='Focus', marca=marca_ford, tipo=tipo_sedan)


@pytest.fixture
def get_marcas():
    marca1, _ = Marca.objects.get_or_create(nombre='BMW')
    marca2, _ = Marca.objects.get_or_create(nombre='Ford')
    return marca1, marca2

@pytest.fixture
def get_tipos():
    tipo1, _ = TipoVehiculo.objects.get_or_create(descripcion='Deportivo')
    tipo2, _ = TipoVehiculo.objects.get_or_create(descripcion='Sedan')
    return tipo1, tipo2

@pytest.fixture
def get_modelos(get_marcas, get_tipos):
    marca_bmw, marca_ford = get_marcas
    tipo_deportivo, tipo_sedan = get_tipos

    modelo1, _ = ModeloVehiculo.objects.get_or_create(
        nombre='X5',
        marca=marca_bmw,
        tipo=tipo_deportivo
    )
    modelo2, _ = ModeloVehiculo.objects.get_or_create(
        nombre='Focus',
        marca=marca_ford,
        tipo=tipo_sedan
    )
    return modelo1, modelo2