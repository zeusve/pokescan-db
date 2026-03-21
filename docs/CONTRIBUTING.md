# Guia de Contribucion

Gracias por tu interes en contribuir a PokeScan DB. Esta guia describe el proceso de desarrollo, convenciones y flujo de trabajo.

---

## Tabla de Contenidos

- [Configuracion del entorno de desarrollo](#configuracion-del-entorno-de-desarrollo)
- [Convenciones de codigo](#convenciones-de-codigo)
- [Flujo de trabajo con Git](#flujo-de-trabajo-con-git)
- [Tests](#tests)
- [Proceso de code review](#proceso-de-code-review)
- [Codigo de conducta](#codigo-de-conducta)

---

## Configuracion del entorno de desarrollo

### 1. Fork y clonar

```bash
git clone <url-de-tu-fork>
cd pokescan-db
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar entorno

```bash
cp .env.example .env
# Editar .env con valores locales
```

### 5. Levantar infraestructura

```bash
docker compose up -d
```

### 6. Ejecutar migraciones

```bash
alembic upgrade head
```

### 7. Verificar que todo funciona

```bash
# Iniciar la app
uvicorn src.main:app --reload

# En otra terminal, ejecutar tests
pytest -v
```

---

## Convenciones de codigo

### Estilo general

- **Python 3.11+** con type hints en todas las funciones publicas
- **Async/await** para todas las operaciones I/O
- **Docstrings** en modulos y funciones publicas (formato Google style)
- Archivos fuente en ingles, documentacion en espanol

### Estructura de archivos

- Un modulo por responsabilidad (SRP)
- Routers en `src/routers/`
- Logica de negocio en archivos raiz de `src/`
- Tests espejo de la estructura de `src/`

### Nombres

| Elemento | Convencion | Ejemplo |
|---|---|---|
| Variables y funciones | snake_case | `get_cards`, `card_master_id` |
| Clases | PascalCase | `UserCard`, `ImageHasher` |
| Constantes | UPPER_SNAKE_CASE | `VECTOR_DIM`, `MAX_RETRIES` |
| Archivos | snake_case | `pokemon_client.py` |
| Tablas BD | snake_case plural | `users`, `cards_master` |

### Principios del proyecto

- **P2 — Zero Hardcoding:** Toda configuracion via variables de entorno
- **P6 — Determinismo:** Misma entrada produce misma salida (especialmente en vision)
- **P8 — Aislamiento de datos:** Cada usuario solo accede a sus propios datos
- **P9 — Idempotencia:** Operaciones de lectura y hashing son idempotentes

### Imports

Orden de imports (seguir PEP 8):

```python
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy import select

# 3. Local
from .database import get_db
from .models import User
```

---

## Flujo de trabajo con Git

### Estrategia de branching

```
master          ← Branch principal, siempre deployable
  └── feature/  ← Ramas de funcionalidad
  └── fix/      ← Ramas de correccion de bugs
  └── docs/     ← Ramas de documentacion
```

### Formato de commits

Los mensajes de commit siguen [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<scope>): <descripcion>
```

**Tipos:**

| Tipo | Descripcion |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Correccion de bug |
| `docs` | Cambios en documentacion |
| `refactor` | Refactorizacion sin cambio funcional |
| `test` | Agregar o modificar tests |
| `chore` | Tareas de mantenimiento |

**Ejemplos:**

```
feat(cae): API: Endpoints de Coleccion
fix(auth): Corregir validacion de token expirado
docs: Actualizar README con instrucciones de instalacion
test(crud): Agregar tests de paginacion
```

### Proceso de contribucion

1. **Crear una rama** desde `master`:
   ```bash
   git checkout -b feature/mi-nueva-funcionalidad
   ```

2. **Desarrollar** con commits atomicos y descriptivos

3. **Ejecutar tests** antes de hacer push:
   ```bash
   pytest -v
   ```

4. **Push** a tu fork:
   ```bash
   git push origin feature/mi-nueva-funcionalidad
   ```

5. **Crear un Pull Request** hacia `master`

---

## Tests

### Ejecutar la suite completa

```bash
pytest -v
```

### Ejecutar tests por categoria

```bash
# Tests de base de datos
pytest tests/test_db.py tests/test_db_setup.py -v

# Tests de seguridad
pytest tests/test_security.py tests/test_auth.py -v

# Tests de modelos
pytest tests/test_models.py -v

# Tests de CRUD
pytest tests/test_crud.py -v

# Tests de API
pytest tests/test_api_collection.py -v

# Tests end-to-end
pytest tests/test_e2e_flow.py -v

# Tests de infraestructura
pytest tests/test_infra.py -v
```

### Ejecutar un test especifico

```bash
pytest tests/test_crud.py::test_create_card_success -v
```

### Estructura de tests

Los tests siguen el patron **Arrange-Act-Assert**:

```python
async def test_create_card_success(db_session, test_user, card_master):
    # Arrange
    card_in = CardCreate(card_master_id=card_master.id, condition="MINT")

    # Act
    card = await crud.create_card(db_session, card_in, test_user.id)

    # Assert
    assert card is not None
    assert card.condition == "MINT"
```

### Fixtures compartidos

Los fixtures principales estan en `tests/conftest.py`:

| Fixture | Descripcion |
|---|---|
| `db_session` | Sesion async de BD (se salta si `DATABASE_URL` no esta definida) |
| `test_user` | Usuario de prueba creado en BD |
| `card_master` | CardMaster de prueba con vector aleatorio |
| `client` | `httpx.AsyncClient` autenticado con dependency override |

### Agregar nuevos tests

1. Crear el archivo en `tests/` con prefijo `test_`
2. Usar fixtures de `conftest.py` cuando sea posible
3. Usar `pytest.mark.asyncio` para tests async
4. Cubrir tanto el happy path como los casos de error

---

## Proceso de code review

### Checklist para PRs

- [ ] Los tests pasan localmente (`pytest -v`)
- [ ] Se agregan tests para funcionalidad nueva
- [ ] El codigo sigue las convenciones del proyecto
- [ ] Las variables de configuracion van en `.env.example`
- [ ] Los modelos de datos tienen migracion de Alembic
- [ ] No hay secrets hardcodeados

### Que se revisa

- **Correctitud:** La implementacion resuelve el problema descrito
- **Tests:** Cobertura adecuada de happy path y edge cases
- **Seguridad:** Sin vulnerabilidades (inyeccion, exposicion de datos, etc.)
- **Performance:** Queries eficientes, uso correcto de eager loading
- **Consistencia:** Sigue los patrones existentes del proyecto

---

## Codigo de conducta

### Nuestro compromiso

Nos comprometemos a crear un entorno abierto y acogedor. Todo participante en el proyecto debe poder colaborar libre de acoso, independientemente de su experiencia, identidad, genero, orientacion sexual, discapacidad, apariencia, raza, etnia, edad o religion.

### Comportamiento esperado

- Usar un lenguaje inclusivo y respetuoso
- Aceptar criticas constructivas con profesionalismo
- Enfocarse en lo mejor para la comunidad y el proyecto
- Mostrar empatia hacia otros miembros

### Comportamiento inaceptable

- Comentarios ofensivos, trolling o ataques personales
- Acoso publico o privado
- Publicar informacion privada de otros sin consentimiento

### Aplicacion

Los mantenedores del proyecto son responsables de aclarar los estandares de comportamiento y tomar acciones correctivas apropiadas ante cualquier comportamiento inaceptable.
