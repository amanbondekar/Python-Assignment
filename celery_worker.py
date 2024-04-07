# celery_worker.py

from celery import Celery

app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# Load task modules from all registered FastAPI apps.
app.autodiscover_tasks(["main"])
