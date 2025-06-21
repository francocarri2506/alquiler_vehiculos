from datetime import timedelta
import pytest


from apps.alquiler.models import Reserva, Alquiler

#########################################################################################################
#                     1)Verificar que las operaciones CRUD funcionan correctamente.                     #
#                3) Probar que los cálculos implementados en la API devuelven resultados correctos.     #
#########################################################################################################

                                #crear

@pytest.mark.django_db
def test_creacion_reserva_exitosa(user_cliente_con_token, datos_reserva):
    cliente, usuario = user_cliente_con_token
    datos = datos_reserva

    data = {
        "vehiculo": str(datos["vehiculo"].id),
        "fecha_inicio": str(datos["fecha_inicio"]),
        "fecha_fin": str(datos["fecha_fin"]),
    }

    response = cliente.post("/api/v1/viewset/reservas/", data=data, format="json")

    assert response.status_code == 201

    data = response.data
    reserva = Reserva.objects.get(id=data["id"])
    vehiculo=reserva.vehiculo
    # Verificaciones básicas
    assert data["estado"] == "pendiente" #por defecto al realizar una reserva queda en estado pendiente
    assert "patente" in data["vehiculo_info"].lower() or "bmw" in data["vehiculo_info"].lower() #verifico los datos del vehiculo

    # Verificar costo por día
    assert vehiculo.precio_por_dia == 10000, f"Costo esperado: 10000, obtenido: {vehiculo.precio_por_dia}"

    # Verificar cantidad de días de reserva
    cantidad_dias = (reserva.fecha_fin - reserva.fecha_inicio).days
    assert cantidad_dias == 4, f"Duración esperada: 4 días, obtenida: {cantidad_dias} días"

    # Verificar monto total
    monto_esperado = cantidad_dias * vehiculo.precio_por_dia
    assert data[
               "monto_total"] == monto_esperado, f"Monto esperado: {monto_esperado}, obtenido: {data['monto_total']}"
    assert data["monto_total"] == 40000  # 4 días * 10.000

    # Verificar sucursal asociada
    assert reserva.sucursal == datos["vehiculo"].sucursal #si no paso una sucursal se usa automaticamente la del vehiculo

    assert reserva.cliente == usuario
    assert reserva.vehiculo == vehiculo


                                    #lista cuando tenia 1 sola reserva:


@pytest.mark.django_db
def test_listado_reservas_cliente(user_cliente_con_token, crear_reserva_valida):

    #establecer
    cliente, _ = user_cliente_con_token #solo uso apliclient al user no lo nesesito

    #actuar
    response = cliente.get("/api/v1/viewset/reservas/") #con el get llamamos al listar del viewset

    #afirmar
    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert any(res["id"] == str(crear_reserva_valida.id) for res in response.data["results"]) #any para recorrer todos los elementos de results


                                #lista del cliente1 con 5 reservas

@pytest.mark.django_db
def test_listado_reservas_cliente(user_cliente_con_token, crear_reservas_cliente):
    cliente, _ = user_cliente_con_token

    response = cliente.get("/api/v1/viewset/reservas/")

    assert response.status_code == 200
    assert len(response.data["results"]) == 5 #cantidad de reservas que tengo en el fixture

    # Verificamos que los IDs de las reservas creadas estén en los resultados
    ids_reservas = [str(res.id) for res in crear_reservas_cliente]
    ids_respuesta = [res["id"] for res in response.data["results"]]

    for id_esperado in ids_reservas:
        assert id_esperado in ids_respuesta



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


#el usuario que no es dueño de la reserva, no puede ver los datos de una reserva


@pytest.mark.django_db
def test_detalle_reserva_cliente_otro(crear_reserva_valida, user_cliente_con_token, user_cliente2_con_token):
    cliente_intruso, user_intruso = user_cliente2_con_token
    cliente_creador, user_creador = user_cliente_con_token
    reserva = crear_reserva_valida #la reserva la creo con el cliente creador

    # Verificamos que los usuarios sean diferentes
    assert user_intruso.id != user_creador.id, (
        f"Los usuarios deberían ser distintos: intruso ID={user_intruso.id}, dueño ID={user_creador.id}"
    )

    # Actuar: usuario intruso intenta acceder al detalle de la reserva
    response = cliente_intruso.get(f"/api/v1/viewset/reservas/{reserva.id}/")


    # Afirmar: debe recibir 403
    assert response.status_code == 403

    assert str(response.data["detail"]) == "Usted no tiene permiso para realizar esta acción."


                            # modificar


@pytest.mark.django_db
def test_actualizar_reserva_cliente(user_cliente_con_token, crear_reserva_valida):
    cliente, _ = user_cliente_con_token
    reserva = crear_reserva_valida

    # Precondición: precio por día conocido
    precio_por_dia = reserva.vehiculo.precio_por_dia
    assert precio_por_dia == 10000

    # Nueva fecha: 2 días más
    nueva_fecha_fin = reserva.fecha_fin + timedelta(days=2)
    data = {
        "fecha_fin": str(nueva_fecha_fin)
    }

    response = cliente.patch(f"/api/v1/viewset/reservas/{reserva.id}/",data=data,format="json")

    assert response.status_code == 200

    # Validar nueva fecha
    assert response.data["fecha_fin"] == str(nueva_fecha_fin)

    # Validar cantidad de días
    nueva_duracion = (nueva_fecha_fin - reserva.fecha_inicio).days
    assert nueva_duracion == 5

    # Validar monto
    monto_esperado = nueva_duracion * precio_por_dia
    assert response.data["monto_total"] == monto_esperado
    assert response.data["monto_total"] == 50000


                                # modificar sin permiso

@pytest.mark.django_db
def test_actualizar_reserva_intruso(user_cliente_con_token, user_cliente2_con_token, crear_reserva_valida):

    cliente_intruso, user_intruso = user_cliente2_con_token
    cliente_creador, user_creador = user_cliente_con_token

    reserva = crear_reserva_valida  # # Esta reserva pertenece a user_cliente_con_token, no a user_cliente2_con_token

    # Verificamos que los usuarios sean diferentes
    assert user_intruso.id != user_creador.id
    assert reserva.cliente == user_creador

    nueva_fecha_fin = reserva.fecha_fin + timedelta(days=2)

    payload = {
        "fecha_fin": str(nueva_fecha_fin)
    }

    response = cliente_intruso.patch(f"/api/v1/viewset/reservas/{reserva.id}/", data=payload, format="json")

    # Verificamos respuesta
    # Debe dar 403 porque intruso no es dueño ni admin
    assert response.status_code == 403
    # con str paso el error detail a string
    assert str(response.data["detail"]) == "Usted no tiene permiso para realizar esta acción."

    # Verificamos que la fecha no haya cambiado
    reserva_actualizada = Reserva.objects.get(id=reserva.id)
    assert reserva_actualizada.fecha_fin == reserva.fecha_fin


        #modificacion falla por la fecha
@pytest.mark.django_db
def test_actualizar_reserva_fecha_invalida(user_cliente_con_token, crear_reserva_valida):
    cliente, _ = user_cliente_con_token
    reserva = crear_reserva_valida

    fecha_invalida = reserva.fecha_inicio - timedelta(days=1)

    response = cliente.patch(f"/api/v1/viewset/reservas/{reserva.id}/",data={"fecha_fin": str(fecha_invalida)},format="json")

    assert response.status_code == 400
    assert response.data["non_field_errors"][0] == "La fecha de inicio debe ser anterior a la fecha de fin."


#modificar una reserva que finalizo (estado finalizada)

@pytest.mark.django_db
def test_no_actualizar_reserva_finalizada(user_cliente_con_token, crear_reserva_valida):
    cliente, _ = user_cliente_con_token
    reserva = crear_reserva_valida

    # cambio el estado, para no hacer otra reserva
    reserva.estado = 'finalizada'
    reserva.save()

    # Validar estado inicial
    assert reserva.estado == 'finalizada'

    nueva_fecha = reserva.fecha_fin + timedelta(days=2)

    # Guardo datos antes del intento de modificación
    fecha_fin_original = reserva.fecha_fin

    response = cliente.patch(f"/api/v1/viewset/reservas/{reserva.id}/",data={"fecha_fin": str(nueva_fecha)},format="json")

    # Verificar el código de error
    assert response.status_code == 400

    # Verifico mensaje de error
    assert "No se puede modificar una reserva finalizada." in response.data["non_field_errors"]

    # Verificamos que no se haya modificado la fecha_fin
    reserva_actualizada = Reserva.objects.get(id=reserva.id)
    assert reserva_actualizada.fecha_fin == fecha_fin_original


    #eliminar

@pytest.mark.django_db
def test_eliminar_reserva_cliente(user_cliente_con_token, crear_reserva_valida):
    cliente, _ = user_cliente_con_token
    reserva = crear_reserva_valida

    # Verificar la reserva existe
    assert Reserva.objects.filter(id=reserva.id).exists()

    # Eliminar la reserva
    response = cliente.delete(f"/api/v1/viewset/reservas/{reserva.id}/")

    # Verificar respuesta HTTP
    assert response.status_code == 204 #se elima

    # Verificar que la reserva ya no existe en la base de datos
    with pytest.raises(Reserva.DoesNotExist):
        Reserva.objects.get(id=reserva.id)


@pytest.mark.django_db
def test_eliminar_reserva_intruso(user_cliente2_con_token, crear_reserva_valida):
    intruso_client, _ = user_cliente2_con_token
    reserva = crear_reserva_valida

    response = intruso_client.delete(f"/api/v1/viewset/reservas/{reserva.id}/")
    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == 403
    assert str(response.data["detail"]) == "Usted no tiene permiso para realizar esta acción."

@pytest.mark.django_db
def test_eliminar_reserva_intruso(user_cliente_con_token, user_cliente2_con_token, crear_reserva_valida):
    cliente_intruso, user_intruso = user_cliente2_con_token
    cliente_creador, user_creador = user_cliente_con_token

    reserva = crear_reserva_valida  # # Esta reserva pertenece a user_cliente_con_token, no a user_cliente2_con_token

    # Verificamos que los usuarios sean diferentes
    assert user_intruso.id != user_creador.id
    assert reserva.cliente == user_creador


    # Intento de eliminación por usuario no dueño
    response = cliente_intruso.delete(f"/api/v1/viewset/reservas/{reserva.id}/")

    # Verificamos respuesta
    assert response.status_code == 403
    assert str(response.data["detail"]) == "Usted no tiene permiso para realizar esta acción."


    # Verificamos que la reserva sigue existiendo
    assert Reserva.objects.filter(id=reserva.id).exists()
