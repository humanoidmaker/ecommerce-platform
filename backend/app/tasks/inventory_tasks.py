"""inventory_tasks — Celery task."""
from __future__ import annotations
from app.tasks.celery_app import celery_app

@celery_app.task(name="app.tasks.inventory_tasks.run")
def run():
    return {"task": "inventory_tasks", "status": "completed"}
