
# 🚗 Sistema de Alquiler de Vehículos - API REST

##  Introducción

Este proyecto consiste en una **API RESTful** desarrollada con **Django Rest Framework (DRF)** para la gestión integral de un sistema de alquiler de vehículos. La API permite registrar vehículos, clientes, sucursales, reservas y alquileres, facilitando la administración y el control de la disponibilidad de los recursos.

Este sistema fue desarrollado como parte del **Laboratorio I y II** de la materia **Desarrollo de APIs con Django**, cumpliendo con las pautas de autenticación, validaciones avanzadas, consumo de APIs externas y pruebas automatizadas.

---

##  Objetivos del Sistema

- Permitir la gestión de vehículos disponibles para alquiler.
- Administrar información de clientes y sucursales.
- Controlar reservas y alquileres activos/finalizados.
- Validar disponibilidad de vehículos en fechas específicas.
- Garantizar coherencia de datos mediante validaciones personalizadas.
- Calcular precios en moneda local y su equivalente en dólares (vía API externa).

---

##   Funcionalidades Principales

###  Gestión de Vehículos
- Alta, baja, modificación y listado de vehículos.
- Relación con modelo, tipo, marca y sucursal.
- Control de disponibilidad según fechas.

###  Gestión de Clientes
- Registro de clientes con autenticación JWT.
- CRUD de usuarios limitado por permisos.

###  Reservas
- Creación de reservas pendientes.
- Validación de fechas y conflictos con otras reservas o alquileres.
- Confirmación de reservas (creación automática de alquiler).
- Cálculo automático de monto total y conversión a dólares.

###  Alquileres
- Registro de alquileres activos o finalizados.
- Asociación con reservas.
- Cálculo de precio final.

###  Sucursales
- Registro y administración de sucursales por provincia, departamento y localidad.
- Validaciones jerárquicas geográficas.

---

##  Validaciones Avanzadas

- Un cliente no puede tener más de una reserva o alquiler activo en el mismo rango de fechas.
- Un vehículo no puede estar reservado ni alquilado en las mismas fechas.
- La localidad debe pertenecer al departamento indicado, y el departamento a la provincia.
- Duplicados de sucursales no permitidos (por nombre, dirección y ubicación).
- No se permite modificar una reserva finalizada.
- Entre muchas otras más

---

##  Seguridad

- **Autenticación JWT** mediante tokens.
- **Permisos basados en grupos (admin / cliente)** usando `DjangoModelPermissions`.
- Protección de endpoints sensibles: solo el dueño de la reserva o un admin puede modificarla/eliminarla.

---

##  API Externa

Se consumen las siguientes APIs externas para enriquecer y validar datos dentro del sistema:

###  Cotización del dólar blue

> https://dolarapi.com/v1/dolares/blue

Se utiliza esta API para obtener el valor actualizado del dólar blue, el cual se emplea para calcular automáticamente el monto total de la reserva en dólares (`monto_usd`) dentro del serializer correspondiente.

###  API de georreferenciación de localidades argentinas

> https://apis.datos.gob.ar/georef/api

Esta API permite obtener la estructura geográfica oficial de Argentina: **provincias**, **departamentos** y **localidades**.  
Los datos se utilizan para validar que las sucursales se creen únicamente en localidades reales.  
Si una localidad no existe en el departamento seleccionado, no se podrá crear la sucursal.

###  Comando de carga de datos geográficos

Este proyecto incluye un comando personalizado para cargar la información territorial argentina directamente desde la API Georef, evitando el ingreso manual.

```bash

#Comando de carga de datos geográficos

python manage.py cargar_localidades
```

- Consulta todas las **provincias**.
- Para cada provincia, obtiene sus **departamentos**.
- Para cada departamento, obtiene sus **localidades**.
- Carga todos estos datos en la base de datos local mediante los modelos `Provincia`, `Departamento` y `Localidad`.

De esta manera, se asegura que el sistema maneje únicamente ubicaciones **válidas y oficiales**.



---

##  Modelos Principales

Todos los modelos utilizan `UUID` como identificador primario.

### Modelo
- `id`, `nombre`, `marca (FK)`, `tipo (FK)`, `es_premium (campo calculado)`

### Vehículo
- `id`, `modelo (FK)`, `patente`, `año`, `precio_por_dia`, `estado`, `sucursal (FK)`

### Cliente (Usuario)
- `id`, `nombre`, `dni`, `email`, `teléfono`, `dirección`

### Reserva
- `id`, `cliente (FK)`, `vehículo (FK)`, `sucursal (FK)`, `fecha_inicio`, `fecha_fin`, `estado`, `monto_total`, `monto_usd`

### Alquiler
- `id`, `cliente (FK)`, `vehículo (FK)`, `sucursal (FK)`, `fecha_inicio`, `fecha_fin`, `monto_total`, `estado`

### Sucursal
- `id`, `nombre`, `provincia`, `departamento`, `localidad`, `dirección`

---


## 📬 Documentación de la API - Postman

La API cuenta con una colección Postman que permite probar todos los endpoints fácilmente, incluyendo autenticación, gestión de vehículos, reservas, alquileres y más.


Podés acceder a la colección completa de endpoints desde el siguiente link público:

>  [Ver colección Postman](https://api-franco.postman.co/workspace/electiva_apis~b6bd5102-be6c-4eae-9757-23d89db24a06/collection/12914552-ea024811-275d-49d1-8ee9-80962eefbf41?action=share&creator=12914552&active-environment=12914552-4aa0f0be-b34b-47e3-b769-eb7ebc938a5f).


---


### 🌍 Variables útiles de entorno

| Variable      | Valor                        |
|---------------|------------------------------|
| `base_url`    | `http://127.0.0.1:8000`       |
| `view-set`    | `http://127.0.0.1:8000/api/v1/viewset`       |
| `token`       | *(Se obtiene luego de hacer login, ver sección autenticación)* |

** Nota**: Para usar endpoints protegidos, primero hacé una solicitud `POST` a `/api/token/` con tu usuario y contraseña, y copiá el `access` token en la variable `token`.

---

##  Endpoints disponibles

La colección Postman está organizada por módulos funcionales del sistema:

**Autenticación**
  - `POST /api/token/`
  - `POST /api/token/refresh/`

**Sucursales**
  - CRUD de sucursales
  - Validación de localidades/provincia/departamento

**Marcas**
  - CRUD de marcas de vehículos

**Tipo Vehículo**
  - CRUD de tipos (Ej: auto, camioneta, SUV)

**Modelo**
  - CRUD de modelos vinculados a marcas y tipos

**Vehículos**
  - Registro y gestión de vehículos
  - Filtro por disponibilidad
  - Cambios de estado (ej: mantenimiento)

**Reservas**
  - Crear reservas con validaciones
  - Ver mis reservas
  - Modificar o cancelar si está pendiente
  - Rechaza duplicaciones o fechas inválidas

**Alquileres**
  - Generados automáticamente desde reservas confirmadas
  - Estado activo o finalizado
  - Cálculo de `monto_total` y validaciones

---


## 🧪 Testing (Laboratorio II)

Se implementaron pruebas automatizadas con **Pytest** que cubren:

- Operaciones CRUD completas sobre reservas
- Validaciones personalizadas en modelos y serializers.
- Cálculos automáticos de precios y conversiones a dólares.
- Permisos y restricciones de acceso.
- Simulación de API externa con `unittest.mock`.



```bash

# Ejemplo para correr los tests:

pytest -v

```

---

##  Requisitos del Proyecto

- Python 3.11+
- Django 5.x
- Django REST Framework
- Pytest + Pytest-Django
- djangorestframework-simplejwt

---

##  Repositorio

📎 [GitHub del Proyecto](https://github.com/francocarri2506/alquiler_vehiculos)

---

##  Autor

Desarrollado por **Carrizo Nicolás Franco**  
Materia: **Desarrollo de Apis - Electiva**  
Docente: *Mgrt. Cecilia E. Gallardo*