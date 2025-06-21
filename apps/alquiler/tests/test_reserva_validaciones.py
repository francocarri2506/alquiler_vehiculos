from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
import pytest
from django.utils import timezone
from rest_framework.exceptions import ErrorDetail

from apps.alquiler.models import Reserva, Alquiler

#########################################################################################################
#      2) Comprobar que las validaciones personalizadas del API (en serializador, modelo o vista)       #
#                                       se comportan como se espera                                     #
#########################################################################################################

#validar que el vehiculo ya tiene una reserva  en esa fecha

@pytest.mark.django_db
def test_crear_reserva_misma_fecha_cliente(user_cliente_con_token, crear_reserva_valida):
    client, user = user_cliente_con_token
    reserva_existente = crear_reserva_valida

    # Verificamos que el vehículo ya tenga una reserva para ese rango
    assert Reserva.objects.filter(
        vehiculo=reserva_existente.vehiculo,
        fecha_inicio__lte=reserva_existente.fecha_fin,
        fecha_fin__gte=reserva_existente.fecha_inicio
    ).exists()

    data = {
        "vehiculo": str(reserva_existente.vehiculo.id),
        "fecha_inicio": str(reserva_existente.fecha_inicio),
        "fecha_fin": str(reserva_existente.fecha_fin),
    }

    response = client.post("/api/v1/viewset/reservas/", data=data, format="json")

    # Verifico que la creación falle por conflicto de fechas
    assert response.status_code == 400
    assert response.data == {
        "non_field_errors": [
            ErrorDetail(string="El vehículo ya tiene una reserva en ese rango de fechas.", code="invalid")
        ]
    }

    # Verifico que no se haya creado una nueva reserva
    cantidad_reservas = Reserva.objects.filter(cliente=user).count()
    assert cantidad_reservas == 1


#evitar que un cliente que ya tiene un alquiler activo o pendiente en ciertas fechas
# pueda hacer una reserva nueva en ese mismo rango, aunque sea para otro vehículo.

@pytest.mark.django_db
def test_crear_reserva_conflicto_alquiler_cliente(user_cliente_con_token, crear_alquiler_valido, get_vehiculos):
    client, cliente = user_cliente_con_token
    alquiler = crear_alquiler_valido

    # uso las fechas del alquiler que tengo como dato, para forzar que sean iguales
    fecha_inicio = alquiler.fecha_inicio
    fecha_fin = alquiler.fecha_fin

    # Usamos el mismo cliente, pero usando otro vehículo (debería igual fallar por cliente con alquiler activo)
    #si uso el mismo vehiculo da otro error de vehiculo no disponible
    vehiculo = get_vehiculos[1]

    # Precondiciones
    assert alquiler.cliente == cliente  #El alquiler debe pertenecer al cliente que está haciendo la reserva
    assert vehiculo != alquiler.vehiculo #El vehículo usado para la reserva debe ser distinto al del alquiler
    assert alquiler.estado in ["pendiente", "activo"]

    # Aseguramos que hay conflicto de fechas entre reserva y alquiler
    assert fecha_inicio <= alquiler.fecha_fin and fecha_fin >= alquiler.fecha_inicio

    data = {
        "vehiculo": str(vehiculo.id),
        "fecha_inicio": str(fecha_inicio),
        "fecha_fin": str(fecha_fin)
    }

    response = client.post("/api/v1/viewset/reservas/", data=data, format="json")

    # Validación de respuesta
    assert response.status_code == 400
    assert response.data == {
        "non_field_errors": [
            "El cliente ya tiene un alquiler activo o pendiente en ese rango de fechas."
        ]
    }

    # Confirmar que no se creó la reserva
    reservas = Reserva.objects.filter(cliente=cliente, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    assert reservas.count() == 0

#########################################################################################################
#                   4) Simular respuestas de APIs externas si se utilizan en la aplicación.             #
#########################################################################################################


#para no hacer la llamada real al API externa uso un mock
@pytest.mark.django_db
#patch:Hace que todas las llamadas a obtener_precio_dolar_blue durante este test usen un valor simulado
@patch("apps.alquiler.api.v1.serializers.obtener_precio_dolar_blue")
def test_reserva_calcula_monto_usd(mock_dolar, user_cliente_con_token, get_vehiculos):
    client, cliente = user_cliente_con_token
    vehiculo = get_vehiculos[0]
    # Aseguramos precio fijo para calcular con precisión
    vehiculo.precio_por_dia = 10000
    vehiculo.save()

    # le doy un valor al dolar, ya que si uso la cotización está constantemente cambiando y me daba error
    mock_dolar.return_value = 1200

    fecha_inicio = timezone.now().date() + timedelta(days=1)
    fecha_fin = fecha_inicio + timedelta(days=3)  # 3 días
    dias = (fecha_fin - fecha_inicio).days

    data = {
        "vehiculo": str(vehiculo.id),
        "fecha_inicio": str(fecha_inicio),
        "fecha_fin": str(fecha_fin),
    }
    #con esto tenemos una reserva de 3 dias a 10000 y dolar a 1200

    response = client.post("/api/v1/viewset/reservas/", data=data, format="json")
    assert response.status_code == 201

    # Validación de monto_total
    monto_total = dias * vehiculo.precio_por_dia
    assert response.data["monto_total"] == monto_total

    # Validación de conversión a USD

    esperado_usd = round(monto_total / mock_dolar.return_value, 2)
    monto_usd_respuesta = float(response.data["monto_usd"])
    assert monto_usd_respuesta == esperado_usd

    # Validación cruzada explícita
    assert monto_usd_respuesta == round((dias * 10000) / 1200, 2)


#probando el action confirmar del viewset de reserva

@pytest.mark.django_db
def test_confirmar_reserva_exitosa(user_cliente_con_token, crear_reserva_valida):
    client, cliente = user_cliente_con_token
    #1 traigo una reserva creada en fixture y no la creo
    reserva = crear_reserva_valida

    assert reserva.estado == 'pendiente'

    alquileres_antes = Alquiler.objects.count()
    # 2. Confirmamos la reserva vía endpoint
    response = client.post("/api/v1/viewset/reservas/{}/confirmar/".format(reserva.id), format="json")

    assert response.status_code == 201
    assert response.data["mensaje"] == "Reserva confirmada y alquiler creado."

    # 3. Verificamos que la reserva haya cambiado su estado
    reserva.refresh_from_db()
    assert reserva.estado == 'confirmada'

    # 4. Verificamos que se creó un alquiler asociado
    alquileres_despues = Alquiler.objects.count()
    assert alquileres_despues == alquileres_antes + 1 #para comprobar su creacion

    alquileres = Alquiler.objects.filter(cliente=cliente, vehiculo=reserva.vehiculo)
    assert alquileres.exists()

    alquiler = alquileres.first()
    assert alquiler.fecha_inicio == reserva.fecha_inicio
    assert alquiler.fecha_fin == reserva.fecha_fin
    assert alquiler.monto_total == Decimal(response.data["alquiler"]["monto_total"])
    assert alquiler.estado == 'activo'

#########################################################################################################
#                                       probando con parametrize                                        #
#########################################################################################################

#field: qué campo o condición se quiere testear.
# value: el valor a usar para esa condición.
# expected_msg: el mensaje de error que se espera recibir de la API

@pytest.mark.django_db
@pytest.mark.parametrize("field, value, expected_msg", [

# Fecha fin anterior a inicio
    ("fecha_fin", (timezone.now().date() + timedelta(days=2), timezone.now().date() + timedelta(days=1)),
     "La fecha de inicio debe ser anterior a la fecha de fin."),

# Reserva mayor a 30 días
    ("fecha_fin", (timezone.now().date(), timezone.now().date() + timedelta(days=31)),
     "La reserva no puede superar los 30 días."),

# Vehículo no disponible
    ("vehiculo_estado", "en_mantenimiento",
     "El vehículo no está disponible para reservar."),

# Vehículo ya reservado en ese rango
    ("vehiculo_reservado", True,
      "El vehículo ya tiene una reserva en ese rango de fechas."),

# Vehículo ya alquilado en ese rango
     ("vehiculo_alquilado", True,
      "El vehículo ya está alquilado en ese rango de fechas."),


# Cliente ya tiene una reserva en ese rango

    ("cliente_ya_reservo", True,
     "El cliente ya tiene una reserva activa o pendiente en ese rango de fechas."),

# Cliente ya tiene un alquiler en ese rango

    ("cliente_ya_alquilo", True,
     "El cliente ya tiene un alquiler activo o pendiente en ese rango de fechas."),
])
def test_validaciones_reserva_parametrizadas(
    user_cliente_con_token,
    get_vehiculos,
    crear_reserva_valida2,
    field, value, expected_msg
):
    client, cliente = user_cliente_con_token
    hoy = timezone.now().date()
    fecha_inicio = hoy + timedelta(days=3)
    fecha_fin = hoy + timedelta(days=5)

    vehiculo1, vehiculo2, vehiculo3 = get_vehiculos
    vehiculo = vehiculo1

    if field == "fecha_fin":
        fecha_inicio, fecha_fin = value

    elif field == "vehiculo_estado":
        vehiculo.estado = value
        vehiculo.save()

    elif field == "vehiculo_reservado":
        crear_reserva_valida2(cliente=cliente, vehiculo=vehiculo,fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

    elif field == "vehiculo_alquilado":
        Alquiler.objects.create(
            cliente=cliente,
            vehiculo=vehiculo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='activo',
            sucursal=vehiculo.sucursal,
            monto_total=vehiculo.precio_por_dia * (fecha_fin - fecha_inicio).days
        )

    elif field == "cliente_ya_reservo":
        crear_reserva_valida2(cliente=cliente, vehiculo=vehiculo2, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

    elif field == "cliente_ya_alquilo":
        Alquiler.objects.create(
            cliente=cliente,
            vehiculo=vehiculo2,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='activo',
            sucursal=vehiculo2.sucursal,
            monto_total=vehiculo2.precio_por_dia * (fecha_fin - fecha_inicio).days
        )

    data = {
        "vehiculo": str(vehiculo.id),
        "fecha_inicio": str(fecha_inicio),
        "fecha_fin": str(fecha_fin),
    }

    response = client.post("/api/v1/viewset/reservas/", data=data, format="json")

    assert response.status_code == 400

    mensaje_error = None
    if "non_field_errors" in response.data:
        mensaje_error = str(response.data["non_field_errors"][0])
    elif "vehiculo" in response.data:
        mensaje_error = str(response.data["vehiculo"][0])
    elif "fecha_inicio" in response.data:
        mensaje_error = str(response.data["fecha_inicio"][0])
    elif "fecha_fin" in response.data:
        mensaje_error = str(response.data["fecha_fin"][0])
    else:
        mensaje_error = str(response.data)

    assert expected_msg in mensaje_error

