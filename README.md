# PokeScan DB

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-0.2.5-4169E1)
![Redis](https://img.shields.io/badge/Redis-Alpine-DC382D?logo=redis&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

Backend API para gestionar colecciones de cartas del Pokemon Trading Card Game (TCG) con capacidades de **busqueda visual por similitud** mediante vectores perceptuales.

---

## Tabla de Contenidos

- [Descripcion](#descripcion)
- [Caracteristicas](#caracteristicas)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Documentacion](#documentacion)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

---

## Descripcion

PokeScan DB es una API REST que permite a los usuarios:

- **Registrar y autenticar** cuentas con JWT
- **Gestionar colecciones** personales de cartas Pokemon TCG
- **Identificar cartas visualmente** mediante hashing perceptual de imagenes (vectores de 512 dimensiones almacenados en pgvector)
- **Sincronizar** colecciones de forma ligera entre dispositivos
- **Consultar** el catalogo oficial de cartas via la API de Pokemon TCG

Cada usuario tiene su propia coleccion aislada con metadatos de condicion, ubicacion y cantidad por carta.

---

## Caracteristicas

- **Autenticacion JWT** con hashing bcrypt de contrasenas
- **CRUD completo** de coleccion de cartas por usuario
- **Busqueda por similitud visual** con pgvector (vectores 512-dim)
- **Hashing perceptual determinista** de imagenes (OpenCV + imagehash)
- **Cliente async** para la API de Pokemon TCG con retry y backoff exponencial
- **Endpoint de sincronizacion ligera** (ORJSONResponse para alto rendimiento)
- **Aislamiento de datos** entre usuarios
- **Async end-to-end**: FastAPI, SQLAlchemy 2.0, asyncpg
- **Migraciones** de base de datos con Alembic
- **Cola de tareas** preparada con Celery + Redis

---

## Tech Stack

| Componente | Tecnologia | Version |
|---|---|---|
| Framework Web | FastAPI + Uvicorn | >= 0.115 |
| Lenguaje | Python | 3.11+ |
| Base de Datos | PostgreSQL + pgvector | 16 |
| ORM | SQLAlchemy (async) | >= 2.0 |
| Migraciones | Alembic | >= 1.13 |
| Autenticacion | python-jose + bcrypt | HS256 |
| Cola de Tareas | Celery + Redis | >= 5.4 |
| Vision | OpenCV + imagehash | >= 4.9 |
| HTTP Client | httpx (async) | >= 0.27 |
| Validacion | Pydantic | >= 2.0 |
| Serializacion | orjson | >= 3.9 |

---

## Quick Start

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd pokescan-db
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus valores (SECRET_KEY, credenciales de BD, etc.)
```

### 3. Levantar servicios con Docker

```bash
docker compose up -d
```

Esto inicia PostgreSQL 16 (con pgvector) y Redis.

### 4. Instalar dependencias e inicializar la BD

```bash
pip install -r requirements.txt
alembic upgrade head
```

### 5. Ejecutar la aplicacion

```bash
uvicorn src.main:app --reload
```

La API estara disponible en `http://localhost:8000`. Verifica con:

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

> Para instrucciones detalladas, consulta [docs/INSTALLATION.md](docs/INSTALLATION.md).

---

## Documentacion

| Documento | Descripcion |
|---|---|
| [Instalacion](docs/INSTALLATION.md) | Guia completa de instalacion y configuracion |
| [Uso](docs/USAGE.md) | Guia de uso con ejemplos practicos |
| [Referencia API](docs/API.md) | Documentacion completa de endpoints |
| [Arquitectura](docs/ARCHITECTURE.md) | Diseno, diagramas y decisiones tecnicas |
| [Contribucion](docs/CONTRIBUTING.md) | Guia para contribuir al proyecto |
| [Changelog](docs/CHANGELOG.md) | Historial de cambios |

---

## Estructura del Proyecto

```
pokescan-db/
├── src/
│   ├── main.py              # Entry point FastAPI
│   ├── database.py          # Engine async + sesion SQLAlchemy
│   ├── models.py            # Modelos ORM (User, CardMaster, UserCard)
│   ├── schemas.py           # Schemas Pydantic
│   ├── security.py          # Auth JWT + bcrypt
│   ├── vision.py            # Hashing perceptual de imagenes
│   ├── pokemon_client.py    # Cliente async API Pokemon TCG
│   ├── crud.py              # Operaciones CRUD de coleccion
│   ├── worker.py            # Configuracion Celery
│   ├── constants.py         # Constantes globales
│   └── routers/
│       └── collection.py    # Endpoints de coleccion
├── tests/                   # Suite de tests (15 archivos)
├── alembic/                 # Migraciones de BD
├── docker-compose.yml       # PostgreSQL + Redis
├── requirements.txt         # Dependencias Python
└── .env.example             # Plantilla de variables de entorno
```

---

## Contribuir

Las contribuciones son bienvenidas. Consulta [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) para conocer el proceso de desarrollo, convenciones y flujo de trabajo.

---

## Licencia

Este proyecto esta bajo la licencia MIT. Consulta el archivo `LICENSE` para mas detalles.

---

## Creditos

- **Lucia** — Desarrollo principal
- [Pokemon TCG API](https://pokemontcg.io/) — Fuente de datos de cartas
- [pgvector](https://github.com/pgvector/pgvector) — Extension de vectores para PostgreSQL
