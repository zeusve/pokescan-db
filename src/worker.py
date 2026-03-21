import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# P2: Zero Hardcode - Usar variable de entorno con fallback para local
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "pokescan",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Importar tareas aquí en el futuro para que el worker las reconozca
# celery_app.autodiscover_tasks(['src.tasks'])
