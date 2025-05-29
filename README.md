# Sistema de Alquiler de Vehículos

1. INTRODUCCION:

Este documento describe los requisitos funcionales y técnicos necesarios para el desarrollo de una API RESTful 
utilizando Django Rest Framework (DRF) para un Sistema de Alquiler de Vehículos. La API permitirá gestionar 
la información sobre vehículos, clientes, reservas y alquileres, ofreciendo endpoints claros para facilitar 
la integración con frontends o sistemas externos.


2. OBJETIVO DEL SISTEMA:

El objetivo del sistema es permitir que una empresa de alquiler de vehículos pueda:

 	Registrar vehículos disponibles para alquiler.
 	Gestionar la información de los clientes.
 	Registrar reservas y alquileres activos o finalizados.
 	Controlar la disponibilidad de los vehículos.
 	Registrar el historial de alquileres.


3. Requisitos Funcionales:

3.1 Gestión de Vehículos
    
    Gestion de modelos
    Gestion de tipos
    Gestion de marcas

3.2 Gestión de Clientes

3.3 Gestión de Alquileres

3.4 Gestión de Reservas

3.5 Gestión de Sucursales



4. Requisitos No Funcionales

La API debe seguir los principios REST.

La API debe devolver respuestas en formato JSON.

La validación de datos debe realizarse a través de serializers.

La API debe contar con control de errores adecuado (vehículo no disponible, fechas inválidas, etc.).

Se debe implementar paginación para los listados largos.

Se recomienda el uso de token de autenticación para acceder a los endpoints protegidos (JWT).


5. Modelo de Datos: en todos los casos se usara uuid

   Modelo:
    
    id

    nombre

    marca (ForeignKey)

    tipo (ForeignKey)

    es_premium (Campo calculado)

   Sucursal

    id

    nombre

    provincia

    departamento

    localidad

    direccion

	Vehículo

 	Id

    modelo FK
   
    patente

    año

    precio por dia

    estado

    sucursal FK

	Cliente

 	Id

 	Nombre

 	Dni

 	Email

 	Teléfono

 	Dirección

	Alquiler

 	Id

 	cliente (FK)

 	vehículo (FK)

    sucursal (FK)

 	fecha_inicio

 	fecha_fin

 	monto_total

 	estado


	Reserva

 	Id

 	cliente (FK)

 	vehículo (FK)

    sucursal (FK)

 	fecha_inicio

 	fecha_fin

 	estado

