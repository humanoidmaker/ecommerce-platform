"""payout_tasks — Celery task."""
from __future__ import annotations
from app.tasks.celery_app import celery_app

@celery_app.task(name="app.tasks.payout_tasks.run")
def run():
    return {"task": "payout_tasks", "status": "completed"}
