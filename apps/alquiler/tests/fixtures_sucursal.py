import pytest
from apps.alquiler.models import Sucursal, Provincia, Departamento, Localidad


@pytest.fixture
def datos_geograficos():
    provincia = Provincia.objects.create(nombre="Córdoba")
    departamento = Departamento.objects.create(nombre="Capital", provincia=provincia)
    localidad = Localidad.objects.create(nombre="Córdoba", departamento=departamento)
    return provincia, departamento, localidad


@pytest.fixture
def crear_sucursales_existentes(db):

    catamarca = Provincia.objects.get_or_create(nombre='Catamarca')[0]
    tucuman = Provincia.objects.get_or_create(nombre='Tucumán')[0]

    santa_maria = Departamento.objects.get_or_create(nombre='Santa María', provincia=catamarca)[0]
    tafi_valle = Departamento.objects.get_or_create(nombre='Tafí del Valle', provincia=tucuman)[0]

    localidad_santa_maria = Localidad.objects.get_or_create(nombre='Santa María', departamento=santa_maria)[0]
    localidad_san_jose = Localidad.objects.get_or_create(nombre='San José', departamento=santa_maria)[0]
    localidad_amaicha = Localidad.objects.get_or_create(nombre='Amaicha del Valle', departamento=tafi_valle)[0]
    """
    Sucursal.objects.create(
        nombre='Auto Rentas',
        provincia=catamarca,
        departamento=santa_maria,
        localidad=localidad_santa_maria,
        direccion='9 de julio 1300'
    )
    Sucursal.objects.create(
        nombre='Auto Rentas',
        provincia=catamarca,
        departamento=santa_maria,
        localidad=localidad_san_jose,
        direccion='Av las Americas'
    )
    Sucursal.objects.create(
        nombre='CarrosSeguros',
        provincia=tucuman,
        departamento=tafi_valle,
        localidad=localidad_amaicha,
        direccion='avenidas las americas'
    )
    Sucursal.objects.create(
        nombre='Renta y Ve',
        provincia=catamarca,
        departamento=santa_maria,
        localidad=localidad_santa_maria,
        direccion='Av las Americas'
    )
    """
    sucursales = [
        Sucursal.objects.create(nombre="Auto Rentas", direccion="9 de julio 1300", provincia=catamarca, departamento=santa_maria, localidad=localidad_santa_maria),
        Sucursal.objects.create(nombre="Auto Rentas", direccion="Av las Americas", provincia=catamarca, departamento=santa_maria, localidad=localidad_san_jose),
        Sucursal.objects.create(nombre="CarrosSeguros", direccion="avenidas las americas", provincia=tucuman, departamento=tafi_valle, localidad=localidad_amaicha),
        Sucursal.objects.create(nombre="Renta y Ve", direccion="Av las Americas", provincia=catamarca, departamento=santa_maria, localidad=localidad_santa_maria),
    ]

    return sucursales


#para probar todos los errores juntos:

@pytest.fixture
def provincia_catamarca(db):
    return Provincia.objects.create(nombre="Catamarca")


@pytest.fixture
def departamento_santa_maria(provincia_catamarca):
    return Departamento.objects.create(nombre="Santa María", provincia=provincia_catamarca)


@pytest.fixture
def localidad_santa_maria(departamento_santa_maria):
    return Localidad.objects.create(nombre="Santa María", departamento=departamento_santa_maria)