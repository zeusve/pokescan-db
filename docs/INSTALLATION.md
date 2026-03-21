# Guia de Instalacion

Guia paso a paso para instalar y configurar PokeScan DB en tu entorno local.

---

## Tabla de Contenidos

- [Prerrequisitos](#prerrequisitos)
- [Instalacion paso a paso](#instalacion-paso-a-paso)
- [Variables de entorno](#variables-de-entorno)
- [Setup de base de datos](#setup-de-base-de-datos)
- [Verificacion de instalacion](#verificacion-de-instalacion)
- [Troubleshooting](#troubleshooting)

---

## Prerrequisitos

| Herramienta | Version minima | Proposito |
|---|---|---|
| Python | 3.11+ | Runtime de la aplicacion |
| Docker + Docker Compose | 24.0+ / 2.20+ | Servicios de infraestructura (PostgreSQL, Redis) |
| pip | 23.0+ | Gestor de paquetes Python |
| Git | 2.40+ | Control de versiones |

### Sistemas operativos compatibles

- Linux (Ubuntu 22.04+, Debian 12+, Fedora 38+)
- macOS 13+ (Ventura o superior)
- Windows 10/11 con WSL2

> **Nota:** Se requiere Docker para ejecutar PostgreSQL 16 con la extension pgvector y Redis. Alternativamente, puedes instalar ambos servicios de forma nativa.

---

## Instalacion paso a paso

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd pokescan-db
```

### 2. Crear un entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux / macOS
# .venv\Scripts\activate   # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus valores. Consulta la [tabla de variables](#variables-de-entorno) mas abajo.

### 5. Levantar servicios de infraestructura

```bash
docker compose up -d
```

Esto inicia:
- **PostgreSQL 16** con pgvector en el puerto `5432`
- **Redis Alpine** en el puerto `6379`

Verifica que ambos servicios estan corriendo:

```bash
docker compose ps
```

### 6. Ejecutar migraciones de base de datos

```bash
alembic upgrade head
```

Esto crea las tablas: `users`, `cards_master` y `user_cards`.

### 7. Iniciar la aplicacion

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. (Opcional) Iniciar el worker de Celery

```bash
celery -A src.worker worker --loglevel=info
```

---

## Variables de entorno

| Variable | Descripcion | Valor por defecto | Obligatoria |
|---|---|---|---|
| `POSTGRES_USER` | Usuario de PostgreSQL | `pokescan_admin` | Si |
| `POSTGRES_PASSWORD` | Contrasena de PostgreSQL | `replace_me_in_production` | Si |
| `POSTGRES_DB` | Nombre de la base de datos | `pokescan` | Si |
| `POSTGRES_HOST` | Host de PostgreSQL | `localhost` | Si |
| `POSTGRES_PORT` | Puerto de PostgreSQL | `5432` | No |
| `DATABASE_URL` | URL de conexion completa a PostgreSQL | `postgresql+asyncpg://postgres:postgres@localhost:5432/pokescan` | Si |
| `SECRET_KEY` | Clave secreta para firmar tokens JWT | `replace_me_with_a_random_secret` | Si |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tiempo de expiracion del token (minutos) | `30` | No |
| `REDIS_URL` | URL de conexion a Redis | `redis://localhost:6379/0` | Si |
| `POKEMON_TCG_API_KEY` | API Key para Pokemon TCG API | — | No |
| `POKEMON_TCG_BASE_URL` | URL base de la API Pokemon TCG | `https://api.pokemontcg.io/v2` | No |

> **Advertencia:** Cambia `SECRET_KEY` y `POSTGRES_PASSWORD` antes de cualquier despliegue. Los valores por defecto son solo para desarrollo local.

### Generar una SECRET_KEY segura

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Setup de base de datos

### Migraciones con Alembic

Las migraciones se encuentran en `alembic/versions/`. El historial de migraciones es:

1. `c10345f90d5a` — Crear tabla `users`
2. `a7b3c8d2e1f4` — Crear tabla `cards_master` con pgvector
3. `b8c4d9e3f2a5` — Actualizar dimension del vector de imagen a 512
4. `20260321` — Crear tabla `user_cards` (inventario)

#### Ejecutar todas las migraciones

```bash
alembic upgrade head
```

#### Ver el estado actual

```bash
alembic current
```

#### Revertir la ultima migracion

```bash
alembic downgrade -1
```

### Extension pgvector

La extension `vector` se instala automaticamente al iniciar el contenedor de PostgreSQL, gracias al script `init.sql`:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Si usas PostgreSQL nativo (sin Docker), instala pgvector manualmente siguiendo la [documentacion oficial](https://github.com/pgvector/pgvector#installation).

---

## Verificacion de instalacion

### 1. Verificar servicios Docker

```bash
docker compose ps
# Ambos servicios deben mostrar "healthy"
```

### 2. Verificar conexion a PostgreSQL

```bash
docker compose exec db psql -U pokescan_admin -d pokescan -c "SELECT 1;"
```

### 3. Verificar extension pgvector

```bash
docker compose exec db psql -U pokescan_admin -d pokescan -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
```

### 4. Verificar conexion a Redis

```bash
docker compose exec redis redis-cli ping
# Debe responder: PONG
```

### 5. Verificar la API

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

### 6. Ejecutar tests

```bash
pytest -v
```

---

## Troubleshooting

### El contenedor de PostgreSQL no arranca

**Sintoma:** `docker compose ps` muestra el servicio `db` como `unhealthy` o `exited`.

**Solucion:**
```bash
# Ver logs del contenedor
docker compose logs db

# Causa comun: puerto 5432 ya en uso
sudo lsof -i :5432
# Detener el proceso que ocupa el puerto, o cambiar POSTGRES_PORT en .env
```

### Error "relation does not exist"

**Sintoma:** SQLAlchemy lanza errores indicando que las tablas no existen.

**Solucion:**
```bash
alembic upgrade head
```

### Error de conexion a la base de datos

**Sintoma:** `asyncpg.exceptions.ConnectionDoesNotExistError` o errores similares.

**Solucion:**
1. Verifica que `DATABASE_URL` en `.env` usa el driver `postgresql+asyncpg://`
2. Confirma que el contenedor de PostgreSQL esta corriendo
3. Asegurate de que el host es `localhost` (no `db`) cuando ejecutas fuera de Docker

### Error "extension vector does not exist"

**Sintoma:** Alembic falla al crear columnas de tipo `Vector`.

**Solucion:**
```bash
# Verificar que usas la imagen pgvector/pgvector:pg16
docker compose exec db psql -U pokescan_admin -d pokescan -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Tests fallan con "DATABASE_URL not set"

**Sintoma:** Los tests de integracion se saltan (`SKIPPED`).

**Solucion:**
```bash
# Asegurate de tener el .env cargado o exporta la variable
export DATABASE_URL="postgresql+asyncpg://pokescan_admin:replace_me_in_production@localhost:5432/pokescan"
pytest -v
```

### Error de importacion de OpenCV

**Sintoma:** `ModuleNotFoundError: No module named 'cv2'`

**Solucion:**
```bash
pip install opencv-python-headless>=4.9.0.80
```

> **Nota:** Se usa la variante `headless` para evitar dependencias de GUI.
