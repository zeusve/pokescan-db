# Changelog

Todos los cambios relevantes de este proyecto estan documentados en este archivo.

El formato esta basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

---

## [0.1.0] - 2026-03-21

Primera version funcional del backend con CRUD completo de coleccion, autenticacion JWT y modulo de vision.

### Added

- **Scaffold inicial** del proyecto con FastAPI, estructura de directorios y configuracion base (`5c91772`)
- **Infraestructura PostgreSQL + pgvector**: Docker Compose con PostgreSQL 16 y extension pgvector, tests de conexion e integracion vectorial (`72bc840`)
- **Seguridad - Hashing de contrasenas**: Modulo de hashing con bcrypt via passlib, funciones `hash_password()` y `verify_password()` (`db260fa`)
- **Seguridad - Utilidades JWT**: Funciones `create_access_token()` y `decode_token()` con HS256, dependencia `get_current_user` para FastAPI (`2e44bbe`)
- **Infraestructura Redis y Celery**: Configuracion de Celery con broker Redis, servicio Redis en Docker Compose con health check (`7a341da`)
- **Cliente Pokemon TCG API**: Cliente HTTP async con httpx, retry con backoff exponencial para rate limit (429) y errores 5xx, soporte de API key opcional (`3e68067`)
- **Motor de hashing de imagenes**: Clase `ImageHasher` con metodos `to_vector()` (512-dim) y `to_phash()`, procesamiento determinista con OpenCV (`1d04509`)
- **Configurar SQLAlchemy y Alembic**: Engine async con asyncpg, session factory, Base ORM, configuracion de Alembic para migraciones (`7aa0541`)
- **Modelo de datos - Usuarios**: Modelo ORM `User` con campos email, username, password hash, migracion de creacion de tabla (`e543f8d`)
- **Modelo de datos - Cards Master**: Modelo ORM `CardMaster` con columna `image_hash` pgvector, migracion de creacion de tabla (`675dcdc`)
- **Actualizacion de vector**: Migracion para escalar dimension de `image_hash` de 64 a 512 (`b8c4d9e3f2a5`)
- **Modelo de datos - User Cards (Inventario)**: Modelo ORM `UserCard` con relaciones bidireccionales, migracion con foreign keys y cascade delete (`409952c`)
- **Endpoints de autenticacion**: Endpoints `POST /auth/register` y `POST /auth/login` con validacion y tests (`2520286`)
- **CRUD de coleccion**: Modulo `crud.py` con operaciones `get_cards`, `get_card`, `create_card`, `update_card`, `delete_card`, `get_card_ids_for_sync` (`3428189`)
- **Endpoints de coleccion**: Router `/cards` con CRUD completo (POST, GET, PATCH, DELETE), todos protegidos con JWT (`1f14f61`)
- **Endpoint de sincronizacion ligera**: `GET /cards/sync` con ORJSONResponse para retorno eficiente de IDs (`3cd3d1d`)
- **Registro de routers**: Integracion de routers `/auth`, `/scan` y `/cards` en la app FastAPI (`790c53d`)
- **Tests de integracion E2E**: Suite completa de tests end-to-end con JWT real, flujo completo de usuario, validacion de aislamiento de datos (`a4727d6`)
