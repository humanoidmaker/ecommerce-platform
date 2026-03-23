"""review_reminder_tasks — Celery task."""
from __future__ import annotations
from app.tasks.celery_app import celery_app

@celery_app.task(name="app.tasks.review_reminder_tasks.run")
def run():
    return {"task": "review_reminder_tasks", "status": "completed"}
