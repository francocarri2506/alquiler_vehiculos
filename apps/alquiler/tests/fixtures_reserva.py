import pytest
from datetime import timedelta
from django.utils import timezone
from apps.alquiler.models import Reserva, Vehiculo, ModeloVehiculo, Marca, TipoVehiculo, Sucursal, Alquiler, Provincia, \
    Departamento


@pytest.fixture
def get_vehiculos(get_modelos, crear_sucursales_existentes):
    modelo1, modelo2 = get_modelos
    sucursales = crear_sucursales_existentes

    vehiculo1 = Vehiculo.objects.create(
        modelo=modelo1,
        patente="AAA111",
        año=2022,
        estado="disponible",
        sucursal=sucursales[0],
        precio_por_dia=10000
    )
    vehiculo2 = Vehiculo.objects.create(
        modelo=modelo2,
        patente="BBB222",
        año=2021,
        estado="disponible",
        sucursal=sucursales[1],
        precio_por_dia=12000
    )
    vehiculo3 = Vehiculo.objects.create(
        patente="XYZ123",
        modelo=modelo1,
        sucursal=sucursales[1],
        precio_por_dia=1000,
        estado='disponible',
        año=2020,
    )
    return vehiculo1, vehiculo2, vehiculo3


@pytest.fixture
def datos_reserva(get_vehiculos):
    hoy = timezone.now().date()

    vehiculo1 = get_vehiculos[0]
    fecha_inicio = hoy + timedelta(days=1)
    fecha_fin = fecha_inicio + timedelta(days=4)  # 4 días

    return {
        "vehiculo": vehiculo1,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin
    }


@pytest.fixture
def crear_reserva_valida(user_cliente_con_token, get_vehiculos):

    #guardo el usuario que mandamos desde el fixture para asociarlo a la reserva
    client, user = user_cliente_con_token
    cliente = user
    vehiculo = get_vehiculos[0]  # uso el 1er vehiculo de la lista

    hoy = timezone.now().date()
    fecha_inicio = hoy + timedelta(days=1) #uso como fecha inicial mañana
    fecha_fin = fecha_inicio + timedelta(days=3)

    #creo una reserva, con los datos traidos desde el fixture mas las fechas
    reserva = Reserva.objects.create(
        cliente=cliente,
        vehiculo=vehiculo,
        sucursal=vehiculo.sucursal,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado='pendiente',
    )
    return reserva



@pytest.fixture
def crear_alquiler_valido(user_cliente_con_token, provincia_catamarca, localidad_santa_maria, departamento_santa_maria,get_vehiculos):
    _, cliente = user_cliente_con_token

    #creo una sucursal

    sucursal = Sucursal.objects.create(
        nombre="Sucursal Central",
        departamento=departamento_santa_maria,
        provincia=provincia_catamarca,
        localidad=localidad_santa_maria,
        direccion="Av. Siempre Viva 123",
    )

    vehiculo = get_vehiculos[0] #asigno el primer vehiculo de la lista

    hoy = timezone.now().date()
    fecha_fin = hoy + timedelta(days=5)
    dias = (fecha_fin - hoy).days
    monto = vehiculo.precio_por_dia * dias

    alquiler = Alquiler.objects.create(
        cliente=cliente,
        vehiculo=vehiculo,
        fecha_inicio=hoy,
        fecha_fin=fecha_fin,
        estado='activo',
        sucursal=sucursal,
        monto_total=monto,  # valor calculado
    )

    return alquiler


@pytest.fixture
def crear_alquiler_valido1(get_vehiculos, user_cliente_con_token):
    vehiculo1, vehiculo2, vehiculo3 = get_vehiculos
    _, cliente = user_cliente_con_token

    hoy = timezone.now().date()
    #fecha_inicio = hoy + timedelta(days=3)
    fecha_fin = hoy + timedelta(days=5)

    # Crear alquiler con vehiculo3
    alquiler = Alquiler.objects.create(
        cliente=cliente,
        vehiculo=vehiculo3,
        fecha_inicio=hoy,
        #fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado='activo',
        sucursal=vehiculo3.sucursal,
        monto_total=vehiculo3.precio_por_dia * 5
    )
    return alquiler


#para  probar todo con parametrize

@pytest.fixture
def crear_reserva_valida2():
    def _crear(cliente, vehiculo, fecha_inicio, fecha_fin):
        return Reserva.objects.create(
            cliente=cliente,
            vehiculo=vehiculo,
            sucursal=vehiculo.sucursal,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='pendiente',
        )
    return _crear



@pytest.fixture
def crear_reservas_cliente(user_cliente_con_token, get_vehiculos):
    client, user = user_cliente_con_token
    vehiculos = get_vehiculos

    hoy = timezone.now().date()
    reservas = []

    for i in range(5):
        fecha_inicio = hoy + timedelta(days=i + 1)
        fecha_fin = fecha_inicio + timedelta(days=2)

        reserva = Reserva.objects.create(
            cliente=user,
            vehiculo=vehiculos[i % len(vehiculos)],  # por si hay menos de 5 vehículos, los reutilizamos
            sucursal=vehiculos[i % len(vehiculos)].sucursal,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='pendiente',
        )
        reservas.append(reserva)

    return reservas