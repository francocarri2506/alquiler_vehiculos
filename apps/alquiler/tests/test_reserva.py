import pytest
from rest_framework.exceptions import ErrorDetail

from apps.alquiler.models import  Reserva
from datetime import timedelta

#-------------------------------------------------------------------------#
#                       RESERVA - operaciones CRUD                        #
#-------------------------------------------------------------------------#

                                #crear
@pytest.mark.django_db
def test_creacion_reserva_exitosa(user_cliente_con_token, datos_reserva):
    cliente = user_cliente_con_token
    datos = datos_reserva

    payload = {
        "vehiculo": str(datos["vehiculo"].id),
        "fecha_inicio": str(datos["fecha_inicio"]),
        "fecha_fin": str(datos["fecha_fin"]),
    }

    response = cliente.post("/api/v1/viewset/reservas/", data=payload, format="json")

    print("STATUS:", response.status_code) #imprimo para saber si el codigo de error era correcto
    print("DATA:", response.data)

    assert response.status_code == 201, response.data

    data = response.data
    assert data["estado"] == "pendiente"
    assert "patente" in data["vehiculo_info"].lower() or "bmw" in data["vehiculo_info"].lower()
    assert data["monto_total"] == 40000  # 4 días * 10.000

    reserva = Reserva.objects.get(id=data["id"])
    assert reserva.sucursal == datos["vehiculo"].sucursal


                                    #lista
@pytest.mark.django_db
def test_listado_reservas_cliente(user_cliente_con_token, crear_reserva_valida):
    cliente, _ = user_cliente_con_token

    response = cliente.get("/api/v1/viewset/reservas/")

    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == 200
    assert len(response.data["results"]) >= 1
    assert any(res["id"] == str(crear_reserva_valida.id) for res in response.data["results"])


                                # detalle
@pytest.mark.django_db
def test_detalle_reserva_cliente(user_cliente_con_token, crear_reserva_valida):
    cliente, _ = user_cliente_con_token
    reserva = crear_reserva_valida

    response = cliente.get(f"/api/v1/viewset/reservas/{reserva.id}/")

    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == 200
    assert response.data["id"] == str(reserva.id)
    assert str(response.data["vehiculo"]) == str(reserva.vehiculo.id)


                            # modificar

@pytest.mark.django_db
def test_actualizar_reserva_cliente(user_cliente_con_token, crear_reserva_valida):
    cliente, _ = user_cliente_con_token
    reserva = crear_reserva_valida

    nueva_fecha_fin = reserva.fecha_fin + timedelta(days=2)

    payload = {
        "fecha_fin": str(nueva_fecha_fin)
    }

    response = cliente.patch(f"/api/v1/viewset/reservas/{reserva.id}/", data=payload, format="json")

    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == 200
    assert response.data["fecha_fin"] == str(nueva_fecha_fin)


                                # modificar sin permiso

@pytest.mark.django_db
def test_actualizar_reserva_intruso(user_cliente_con_token_intruso, crear_reserva_valida):
    intruso_client, intruso_user = user_cliente_con_token_intruso
    reserva = crear_reserva_valida  # Esta reserva pertenece a otro cliente, no al intruso

    nueva_fecha_fin = reserva.fecha_fin + timedelta(days=2)

    payload = {
        "fecha_fin": str(nueva_fecha_fin)
    }

    response = intruso_client.patch(f"/api/v1/viewset/reservas/{reserva.id}/", data=payload, format="json")

    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    # Debe dar 403 porque intruso no es dueño ni admin
    assert response.status_code == 403
    assert "permiso" in response.data.get('detail', '').lower()
    #assert response.data["detail"] == "No tienes permiso para realizar esta acción."
    #con str paso el error detail a string
    assert str(response.data["detail"]) == "Usted no tiene permiso para realizar esta acción."



                        #eliminar
@pytest.mark.django_db
def test_eliminar_reserva_cliente(user_cliente_con_token, crear_reserva_valida):
    cliente, _ = user_cliente_con_token
    reserva = crear_reserva_valida

    response = cliente.delete(f"/api/v1/viewset/reservas/{reserva.id}/")
    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == 204


@pytest.mark.django_db
def test_eliminar_reserva_intruso(user_cliente_con_token_intruso, crear_reserva_valida):
    intruso_client, _ = user_cliente_con_token_intruso
    reserva = crear_reserva_valida

    response = intruso_client.delete(f"/api/v1/viewset/reservas/{reserva.id}/")
    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == 403
    assert str(response.data["detail"]) == "Usted no tiene permiso para realizar esta acción."


@pytest.mark.django_db
def test_crear_reserva_misma_fecha_cliente(user_cliente_con_token, crear_reserva_valida):
    client, user = user_cliente_con_token
    reserva = crear_reserva_valida

    data = {
        "vehiculo": reserva.vehiculo.id,
        "fecha_inicio": str(reserva.fecha_inicio),
        "fecha_fin": str(reserva.fecha_fin),
    }

    response = client.post("/api/v1/viewset/reservas/", data=data, format="json")


    assert response.status_code == 400
    assert response.data == {
        "non_field_errors": [
            ErrorDetail(string="El vehículo ya tiene una reserva en ese rango de fechas.", code="invalid")
        ]
    }






@pytest.mark.django_db
def test_crear_reserva_conflicto_alquiler_cliente(user_cliente_con_token, crear_alquiler_valido, get_vehiculos):
    client, cliente = user_cliente_con_token
    alquiler = crear_alquiler_valido
    vehiculo = get_vehiculos[1]  #

    data = {
        "vehiculo": str(vehiculo.id),  # ojo acá, pasar el id, no el objeto
        "fecha_inicio": str(alquiler.fecha_inicio),
        "fecha_fin": str(alquiler.fecha_fin)
    }

    response = client.post("/api/v1/viewset/reservas/", data=data, format="json")

    assert response.status_code == 400
    assert response.data == {
        "non_field_errors": [
            "El cliente ya tiene un alquiler activo o pendiente en ese rango de fechas."
        ]
    }

@pytest.mark.django_db
def test_crear_reserva_conflicto_alquiler_cliente(user_cliente_con_token, crear_alquiler_valido1, get_vehiculos):
    client, cliente = user_cliente_con_token
    alquiler = crear_alquiler_valido1
    vehiculo = get_vehiculos[2]  # vehiculo3, el que ya está alquilado en el fixture

    data = {
        "vehiculo": str(vehiculo.id),
        "fecha_inicio": str(alquiler.fecha_inicio),
        "fecha_fin": str(alquiler.fecha_fin)
    }

    response = client.post("/api/v1/viewset/reservas/", data=data, format="json")

    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == 400
    assert response.data == {
        "non_field_errors": [
            "El cliente ya tiene un alquiler activo o pendiente en ese rango de fechas."
        ]
    }




@pytest.mark.django_db
def test_crear_reserva_conflicto_alquiler_cliente(user_cliente_con_token, crear_alquiler_valido,get_vehiculos):
    client, cliente = user_cliente_con_token
    alquiler = crear_alquiler_valido
    vehiculo = get_vehiculos[1]

    data = {
        "vehiculo": vehiculo,
        "fecha_inicio": str(alquiler.fecha_inicio),
        "fecha_fin": str(alquiler.fecha_fin)
    }

    response = client.post("/api/v1/viewset/reservas/", data=data, format="json")

    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == 400
    assert response.data == {
        "non_field_errors": [

            "El cliente ya tiene un alquiler activo o pendiente en ese rango de fechas."

        ]
    }