# Guia de Uso

Guia practica para interactuar con la API de PokeScan DB, con ejemplos reales de request/response.

---

## Tabla de Contenidos

- [Flujo general](#flujo-general)
- [Autenticacion](#autenticacion)
- [Gestion de coleccion](#gestion-de-coleccion)
- [Sincronizacion](#sincronizacion)
- [Casos de uso comunes](#casos-de-uso-comunes)
- [Configuracion avanzada](#configuracion-avanzada)

---

## Flujo general

El flujo tipico de uso de PokeScan DB sigue estos pasos:

```mermaid
sequenceDiagram
    actor U as Usuario
    participant API as PokeScan DB
    participant DB as PostgreSQL

    U->>API: POST /auth/register
    API->>DB: Crear usuario
    API-->>U: Usuario creado

    U->>API: POST /auth/login
    API-->>U: JWT Token

    U->>API: POST /cards/ (con JWT)
    API->>DB: Insertar carta en coleccion
    API-->>U: Carta creada

    U->>API: GET /cards/ (con JWT)
    API->>DB: Consultar coleccion
    API-->>U: Lista de cartas paginada
```

1. **Registrar** una cuenta de usuario
2. **Iniciar sesion** para obtener un token JWT
3. **Usar el token** en todas las peticiones subsecuentes
4. **Gestionar** la coleccion de cartas (crear, listar, actualizar, eliminar)

---

## Autenticacion

Todos los endpoints (excepto `/health`, `/auth/register` y `/auth/login`) requieren un token JWT en el header `Authorization`.

### Registrar un usuario

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ash@pokemon.com",
    "username": "ash_ketchum",
    "password": "pikachu123"
  }'
```

**Respuesta exitosa (201):**

```json
{
  "id": 1,
  "email": "ash@pokemon.com",
  "username": "ash_ketchum",
  "is_active": true
}
```

### Iniciar sesion

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ash_ketchum",
    "password": "pikachu123"
  }'
```

**Respuesta exitosa (200):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Usar el token

Incluye el token en todas las peticiones protegidas:

```bash
curl -X GET http://localhost:8000/cards/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

> **Nota:** El token expira despues de 30 minutos por defecto (configurable con `ACCESS_TOKEN_EXPIRE_MINUTES`).

---

## Gestion de coleccion

### Agregar una carta a la coleccion

```bash
curl -X POST http://localhost:8000/cards/ \
  -H "Authorization: Bearer <tu-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "card_master_id": 1,
    "condition": "MINT",
    "location": "Binder A, Page 3",
    "quantity": 2
  }'
```

**Respuesta exitosa (201):**

```json
{
  "id": 1,
  "card_master_id": 1,
  "condition": "MINT",
  "location": "Binder A, Page 3",
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

> **Nota:** El `card_master_id` debe referenciar un registro existente en la tabla `cards_master`. Si no existe, la API devuelve un error 404.

### Listar cartas de la coleccion

```bash
curl -X GET "http://localhost:8000/cards/?limit=10&offset=0" \
  -H "Authorization: Bearer <tu-token>"
```

**Respuesta exitosa (200):**

```json
[
  {
    "id": 1,
    "card_master_id": 1,
    "condition": "MINT",
    "location": "Binder A, Page 3",
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

**Parametros de paginacion:**

| Parametro | Tipo | Rango | Default | Descripcion |
|---|---|---|---|---|
| `limit` | int | 1 - 100 | 20 | Cantidad de resultados por pagina |
| `offset` | int | >= 0 | 0 | Posicion de inicio |

### Obtener una carta especifica

```bash
curl -X GET http://localhost:8000/cards/1 \
  -H "Authorization: Bearer <tu-token>"
```

**Respuesta exitosa (200):**

```json
{
  "id": 1,
  "card_master_id": 1,
  "condition": "MINT",
  "location": "Binder A, Page 3",
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

### Actualizar una carta

Soporta actualizacion parcial (solo los campos enviados se modifican).

```bash
curl -X PATCH http://localhost:8000/cards/1 \
  -H "Authorization: Bearer <tu-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "condition": "NEAR_MINT",
    "quantity": 3
  }'
```

**Respuesta exitosa (200):**

```json
{
  "id": 1,
  "card_master_id": 1,
  "condition": "NEAR_MINT",
  "location": "Binder A, Page 3",
  "quantity": 3,
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

### Eliminar una carta

```bash
curl -X DELETE http://localhost:8000/cards/1 \
  -H "Authorization: Bearer <tu-token>"
```

**Respuesta exitosa:** `204 No Content` (sin cuerpo de respuesta).

---

## Sincronizacion

El endpoint de sincronizacion devuelve una lista plana de IDs de `card_master` para sincronizacion ligera entre dispositivos.

```bash
curl -X GET http://localhost:8000/cards/sync \
  -H "Authorization: Bearer <tu-token>"
```

**Respuesta exitosa (200):**

```json
[1, 3, 7, 15, 22]
```

Este endpoint usa `ORJSONResponse` para maximizar el rendimiento en colecciones grandes.

---

## Casos de uso comunes

### Inventariar una coleccion fisica

1. Registrar una cuenta
2. Buscar cartas en el catalogo (las cartas maestras deben existir en `cards_master`)
3. Agregar cada carta con su condicion y ubicacion fisica
4. Usar el listado paginado para revisar el inventario

### Sincronizar entre dispositivos

1. Desde el dispositivo principal, agregar cartas a la coleccion
2. Desde otro dispositivo, llamar a `GET /cards/sync` para obtener los IDs
3. Comparar con el estado local y descargar solo las diferencias

### Seguimiento de condicion

Actualizar la condicion de una carta cuando cambie:

```bash
# La carta paso de MINT a PLAYED despues de un torneo
curl -X PATCH http://localhost:8000/cards/42 \
  -H "Authorization: Bearer <tu-token>" \
  -H "Content-Type: application/json" \
  -d '{"condition": "PLAYED"}'
```

---

## Configuracion avanzada

### Tiempo de expiracion del token

Ajusta `ACCESS_TOKEN_EXPIRE_MINUTES` en el archivo `.env`:

```bash
ACCESS_TOKEN_EXPIRE_MINUTES=60  # Token valido por 1 hora
```

### Conexion a la API de Pokemon TCG

Para obtener una API key gratuita, visita [pokemontcg.io](https://pokemontcg.io/) y configurala en `.env`:

```bash
POKEMON_TCG_API_KEY=tu_api_key_aqui
POKEMON_TCG_BASE_URL=https://api.pokemontcg.io/v2
```

La API key aumenta los limites de tasa (rate limits) de la API de Pokemon TCG.

### Worker de Celery

Para tareas en segundo plano (procesamiento de imagenes, sincronizacion masiva):

```bash
celery -A src.worker worker --loglevel=info
```

> **Nota:** El worker de Celery esta configurado pero aun no tiene tareas registradas. Es infraestructura preparada para futuras funcionalidades.

### Modo debug de SQLAlchemy

El engine de SQLAlchemy tiene `echo=True` por defecto, lo que muestra las queries SQL en la consola. Para produccion, se recomienda configurarlo como `False`.

### Documentacion interactiva

FastAPI genera documentacion interactiva automaticamente:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
