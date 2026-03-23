"""abandoned_cart_tasks — Celery task."""
from __future__ import annotations
from app.tasks.celery_app import celery_app

@celery_app.task(name="app.tasks.abandoned_cart_tasks.run")
def run():
    return {"task": "abandoned_cart_tasks", "status": "completed"}
