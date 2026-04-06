# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-04-06T11:30:30.797Z
> Files: 54 tracked | Anatomy hits: 0 | Misses: 0

## ./

- `.gitignore` — Git ignore rules (~10 tok)
- `=3.9.0` (~272 tok)
- `alembic.ini` (~166 tok)
- `CLAUDE.md` — OpenWolf (~57 tok)
- `docker-compose.yml` — Docker Compose services (~206 tok)
- `init.sql` (~12 tok)
- `PROJECT_CONTEXT.md` — PROJECT_CONTEXT — pokescan-db (~3619 tok)
- `README.md` — Project documentation (~1366 tok)
- `requirements.txt` — Python dependencies (~99 tok)

## .claude/

- `settings.json` (~441 tok)
- `settings.local.json` (~36 tok)

## .claude/rules/

- `openwolf.md` (~313 tok)

## .pytest_cache/v/cache/

- `lastfailed` (~204 tok)
- `nodeids` (~1432 tok)

## alembic/

- `env.py` — Alembic environment configuration for async SQLAlchemy migrations. (~577 tok)
- `script.py.mako` (~170 tok)

## alembic/versions/

- `20260321_create_user_cards.py` — create user_cards table (~469 tok)
- `a7b3c8d2e1f4_create_cards_master_table.py` — create cards_master table (~446 tok)
- `b8c4d9e3f2a5_update_card_master_vector_dim.py` — update card_master vector dimension to match ImageHasher.VECTOR_DIM (~231 tok)
- `c10345f90d5a_create_users_table.py` — create users table (~361 tok)

## docs/

- `API.md` — Referencia de API (~2596 tok)
- `ARCHITECTURE.md` — Arquitectura del Proyecto (~3177 tok)
- `CHANGELOG.md` — Change log (~714 tok)
- `CONTRIBUTING.md` — Guia de Contribucion (~1793 tok)
- `INSTALLATION.md` — Guia de Instalacion (~1695 tok)
- `USAGE.md` — Guia de Uso (~1907 tok)

## src/

- `__init__.py` (~0 tok)
- `constants.py` — Project-wide constants (P2 — zero hardcoding). (~88 tok)
- `crud.py` — CRUD operations for the user card collection (SRP: database logic only). (~993 tok)
- `database.py` — Async SQLAlchemy engine, session factory, and declarative base. (~227 tok)
- `main.py` — FastAPI application entry point — router registration only. (~112 tok)
- `models.py` — SQLAlchemy ORM models for pokescan-db entities. (~792 tok)
- `pokemon_client.py` — Client for the Pokémon TCG API (https://pokemontcg.io). (~1264 tok)
- `schemas.py` — Pydantic schemas for request/response validation. (~423 tok)
- `security.py` — hash_password, verify_password, create_access_token, decode_token + 1 more (~700 tok)
- `vision.py` — Vision module: deterministic image hashing for visual similarity search. (~601 tok)
- `worker.py` (~164 tok)

## src/routers/

- `__init__.py` (~0 tok)
- `collection.py` — Router for card collection CRUD endpoints. (~881 tok)

## tests/

- `__init__.py` (~0 tok)
- `conftest.py` — Shared pytest fixtures for the pokescan-db test suite. (~620 tok)
- `test_api_collection.py` — Integration tests for the /cards/ collection API resource. (~3044 tok)
- `test_auth.py` — Integration tests for authentication endpoints. (~598 tok)
- `test_crud.py` — Integration tests for card collection CRUD endpoints. (~2148 tok)
- `test_db_setup.py` — Tests for async SQLAlchemy database setup. (~292 tok)
- `test_db.py` — Tests: connection_succeeds, pgvector_extension_available, vector_column_operations (~425 tok)
- `test_e2e_flow.py` — End-to-end integration tests validating the full user workflow. (~1990 tok)
- `test_health.py` — Tests: health (~10 tok)
- `test_infra.py` — Tests: redis_connection, celery_app_config, celery_broker_uses_env, redis_url_from_env (~364 tok)
- `test_models.py` — Tests for SQLAlchemy ORM models (User, CardMaster, UserCard). (~2972 tok)
- `test_pokemon_client.py` — Tests for PokemonTCGClient. (~1874 tok)
- `test_router_registration.py` — Integration test: verify all routers are registered with correct prefixes. (~381 tok)
- `test_security.py` — Tests: hash_not_plaintext, hash_is_bcrypt_format, hash_is_nondeterministic, verify_correct_password + 8 more (~672 tok)
- `test_vision.py` — Tests for src.vision — ImageHasher vector generation and perceptual hashing. (~1362 tok)
