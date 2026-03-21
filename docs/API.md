# Referencia de API

Documentacion completa de todos los endpoints de PokeScan DB.

**URL base:** `http://localhost:8000`

---

## Tabla de Contenidos

- [Autenticacion](#autenticacion)
- [Health](#health)
- [Auth](#auth)
- [Collection (Cards)](#collection-cards)
- [Scan](#scan)
- [Codigos de error globales](#codigos-de-error-globales)

---

## Autenticacion

La API utiliza **JWT Bearer Token** para autenticacion. Todos los endpoints bajo `/cards` y `/scan` requieren el header:

```
Authorization: Bearer <token>
```

El token se obtiene mediante el endpoint `POST /auth/login` y tiene una validez de 30 minutos por defecto.

### Estructura del token JWT

| Campo | Descripcion |
|---|---|
| `sub` | ID del usuario (string) |
| `exp` | Timestamp de expiracion (UTC) |

### Respuesta de error de autenticacion

Cualquier endpoint protegido devuelve el siguiente error si el token es invalido, expirado o ausente:

```json
{
  "detail": "Invalid or expired token"
}
```

**Codigo HTTP:** `401 Unauthorized`

---

## Health

### `GET /health`

Verifica que la aplicacion esta corriendo.

**Autenticacion:** No requerida

**Parametros:** Ninguno

**Ejemplo de request:**

```bash
curl http://localhost:8000/health
```

**Respuesta exitosa (200):**

```json
{
  "status": "ok"
}
```

---

## Auth

Endpoints de registro e inicio de sesion.

### `POST /auth/register`

Registra un nuevo usuario.

**Autenticacion:** No requerida

#### Body (JSON)

| Campo | Tipo | Obligatorio | Descripcion |
|---|---|---|---|
| `email` | string (email) | Si | Correo electronico (unico) |
| `username` | string | Si | Nombre de usuario (unico) |
| `password` | string | Si | Contrasena en texto plano |

#### Ejemplo de request

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ash@pokemon.com",
    "username": "ash_ketchum",
    "password": "pikachu123"
  }'
```

#### Respuesta exitosa (201)

```json
{
  "id": 1,
  "email": "ash@pokemon.com",
  "username": "ash_ketchum",
  "is_active": true
}
```

#### Errores

| Codigo | Detalle | Causa |
|---|---|---|
| 400 | Email already registered | El email ya esta en uso |
| 422 | Validation Error | Campos faltantes o formato invalido |

---

### `POST /auth/login`

Inicia sesion y devuelve un token JWT.

**Autenticacion:** No requerida

#### Body (JSON)

| Campo | Tipo | Obligatorio | Descripcion |
|---|---|---|---|
| `username` | string | Si | Nombre de usuario |
| `password` | string | Si | Contrasena |

#### Ejemplo de request

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ash_ketchum",
    "password": "pikachu123"
  }'
```

#### Respuesta exitosa (200)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzExMDI3MDAwfQ...",
  "token_type": "bearer"
}
```

#### Errores

| Codigo | Detalle | Causa |
|---|---|---|
| 401 | Invalid credentials | Usuario o contrasena incorrectos |
| 422 | Validation Error | Campos faltantes |

---

## Collection (Cards)

Endpoints para gestionar la coleccion de cartas del usuario autenticado. Todos requieren autenticacion JWT.

> **Aislamiento de datos:** Cada usuario solo puede ver y modificar sus propias cartas. Un usuario no puede acceder a las cartas de otro.

---

### `POST /cards/`

Agrega una carta a la coleccion del usuario.

**Autenticacion:** Requerida

#### Body (JSON)

| Campo | Tipo | Obligatorio | Default | Descripcion |
|---|---|---|---|---|
| `card_master_id` | int | Si | — | ID del registro en `cards_master` |
| `condition` | string | No | `"UNKNOWN"` | Estado de la carta |
| `location` | string | No | `""` | Ubicacion fisica |
| `quantity` | int | No | `1` | Cantidad de copias |

#### Ejemplo de request

```bash
curl -X POST http://localhost:8000/cards/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "card_master_id": 1,
    "condition": "MINT",
    "location": "Binder A",
    "quantity": 2
  }'
```

#### Respuesta exitosa (201)

```json
{
  "id": 1,
  "card_master_id": 1,
  "condition": "MINT",
  "location": "Binder A",
  "quantity": 2,
  "created_at": "2026-03-21T10:30:00+00:00",
  "card_master": {
    "id": 1,
    "api_id": "base1-58",
    "name": "Pikachu",
    "set_id": "base1",
    "rarity": "Common"
  }
}
```

#### Errores

| Codigo | Detalle | Causa |
|---|---|---|
| 401 | Invalid or expired token | Token JWT invalido o expirado |
| 404 | Card master not found | `card_master_id` no existe |
| 422 | Validation Error | Payload invalido |

---

### `GET /cards/`

Lista las cartas de la coleccion del usuario con paginacion.

**Autenticacion:** Requerida

#### Query Parameters

| Parametro | Tipo | Rango | Default | Descripcion |
|---|---|---|---|---|
| `limit` | int | 1 - 100 | 20 | Resultados por pagina |
| `offset` | int | >= 0 | 0 | Posicion de inicio |

#### Ejemplo de request

```bash
curl -X GET "http://localhost:8000/cards/?limit=10&offset=0" \
  -H "Authorization: Bearer <token>"
```

#### Respuesta exitosa (200)

```json
[
  {
    "id": 1,
    "card_master_id": 1,
    "condition": "MINT",
    "location": "Binder A",
    "quantity": 2,
    "created_at": "2026-03-21T10:30:00+00:00",
    "card_master": {
      "id": 1,
      "api_id": "base1-58",
      "name": "Pikachu",
      "set_id": "base1",
      "rarity": "Common"
    }
  }
]
```

Devuelve un array vacio `[]` si la coleccion esta vacia.

#### Errores

| Codigo | Detalle | Causa |
|---|---|---|
| 401 | Invalid or expired token | Token JWT invalido o expirado |
| 422 | Validation Error | Parametros de paginacion fuera de rango |

---

### `GET /cards/{card_id}`

Obtiene los detalles de una carta especifica.

**Autenticacion:** Requerida

#### Path Parameters

| Parametro | Tipo | Descripcion |
|---|---|---|
| `card_id` | int | ID de la carta en la coleccion del usuario |

#### Ejemplo de request

```bash
curl -X GET http://localhost:8000/cards/1 \
  -H "Authorization: Bearer <token>"
```

#### Respuesta exitosa (200)

```json
{
  "id": 1,
  "card_master_id": 1,
  "condition": "MINT",
  "location": "Binder A",
  "quantity": 2,
  "created_at": "2026-03-21T10:30:00+00:00",
  "card_master": {
    "id": 1,
    "api_id": "base1-58",
    "name": "Pikachu",
    "set_id": "base1",
    "rarity": "Common"
  }
}
```

#### Errores

| Codigo | Detalle | Causa |
|---|---|---|
| 401 | Invalid or expired token | Token JWT invalido o expirado |
| 404 | Card not found | La carta no existe o pertenece a otro usuario |

---

### `PATCH /cards/{card_id}`

Actualiza parcialmente una carta de la coleccion.

**Autenticacion:** Requerida

#### Path Parameters

| Parametro | Tipo | Descripcion |
|---|---|---|
| `card_id` | int | ID de la carta en la coleccion del usuario |

#### Body (JSON) — Todos opcionales

| Campo | Tipo | Descripcion |
|---|---|---|
| `condition` | string | Nuevo estado de la carta |
| `location` | string | Nueva ubicacion fisica |
| `quantity` | int | Nueva cantidad |

Solo los campos enviados se actualizan. Los campos omitidos conservan su valor actual.

#### Ejemplo de request

```bash
curl -X PATCH http://localhost:8000/cards/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"condition": "PLAYED", "quantity": 1}'
```

#### Respuesta exitosa (200)

```json
{
  "id": 1,
  "card_master_id": 1,
  "condition": "PLAYED",
  "location": "Binder A",
  "quantity": 1,
  "created_at": "2026-03-21T10:30:00+00:00",
  "card_master": {
    "id": 1,
    "api_id": "base1-58",
    "name": "Pikachu",
    "set_id": "base1",
    "rarity": "Common"
  }
}
```

#### Errores

| Codigo | Detalle | Causa |
|---|---|---|
| 401 | Invalid or expired token | Token JWT invalido o expirado |
| 404 | Card not found | La carta no existe o pertenece a otro usuario |
| 422 | Validation Error | Payload invalido |

---

### `DELETE /cards/{card_id}`

Elimina una carta de la coleccion.

**Autenticacion:** Requerida

#### Path Parameters

| Parametro | Tipo | Descripcion |
|---|---|---|
| `card_id` | int | ID de la carta en la coleccion del usuario |

#### Ejemplo de request

```bash
curl -X DELETE http://localhost:8000/cards/1 \
  -H "Authorization: Bearer <token>"
```

#### Respuesta exitosa

**Codigo:** `204 No Content` (sin cuerpo de respuesta)

#### Errores

| Codigo | Detalle | Causa |
|---|---|---|
| 401 | Invalid or expired token | Token JWT invalido o expirado |
| 404 | Card not found | La carta no existe o pertenece a otro usuario |

---

### `GET /cards/sync`

Devuelve una lista plana de `card_master_id` para sincronizacion ligera.

**Autenticacion:** Requerida

**Parametros:** Ninguno

#### Ejemplo de request

```bash
curl -X GET http://localhost:8000/cards/sync \
  -H "Authorization: Bearer <token>"
```

#### Respuesta exitosa (200)

```json
[1, 3, 7, 15, 22]
```

Devuelve un array vacio `[]` si la coleccion esta vacia.

> **Nota:** Este endpoint usa `ORJSONResponse` para maximizar el rendimiento de serializacion en colecciones grandes.

#### Errores

| Codigo | Detalle | Causa |
|---|---|---|
| 401 | Invalid or expired token | Token JWT invalido o expirado |

---

## Scan

Modulo de vision para procesamiento de imagenes de cartas.

> **Nota:** El router `/scan` esta registrado pero actualmente no tiene endpoints publicos definidos. La logica de hashing esta disponible internamente via la clase `ImageHasher`.

### Funcionalidad interna: ImageHasher

| Metodo | Entrada | Salida | Descripcion |
|---|---|---|---|
| `to_vector(image_bytes)` | bytes | list[float] (512-dim) | Vector normalizado para busqueda por similitud |
| `to_phash(image_bytes)` | bytes | string (hex, 16 chars) | Hash perceptual de 64 bits |

---

## Codigos de error globales

| Codigo | Significado | Descripcion |
|---|---|---|
| 401 | Unauthorized | Token JWT ausente, invalido o expirado |
| 404 | Not Found | Recurso no encontrado o sin permisos |
| 422 | Unprocessable Entity | Error de validacion de Pydantic |
| 500 | Internal Server Error | Error inesperado del servidor |

### Formato de errores de validacion (422)

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### Formato de errores generales

```json
{
  "detail": "Mensaje descriptivo del error"
}
```
