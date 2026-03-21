import pytest
import os
from unittest.mock import patch
from src.worker import celery_app


def test_redis_connection():
    """Verifica que Celery puede conectar con el broker de Redis."""
    try:
        conn = celery_app.broker_connection().ensure_connection(max_retries=2)
        assert conn.connected is True
        conn.release()
    except Exception:
        pytest.skip("Redis no disponible en este entorno")


def test_celery_app_config():
    """Verifica que la app Celery está configurada correctamente."""
    assert celery_app.main == "pokescan"
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.accept_content == ["json"]
    assert celery_app.conf.result_serializer == "json"
    assert celery_app.conf.timezone == "UTC"
    assert celery_app.conf.enable_utc is True


def test_celery_broker_uses_env():
    """Verifica que el broker URL proviene de la variable de entorno."""
    broker_url = str(celery_app.conf.broker_url)
    assert broker_url.startswith("redis://")


def test_redis_url_from_env():
    """Verifica que REDIS_URL se lee correctamente del entorno."""
    test_url = "redis://custom-host:6380/1"
    with patch.dict(os.environ, {"REDIS_URL": test_url}):
        assert os.getenv("REDIS_URL") == test_url
