from __future__ import annotations
from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()
celery_app = Celery("ecommerce", broker=settings.celery_broker_url, backend=settings.celery_result_backend)
celery_app.conf.update(task_serializer="json", accept_content=["json"], result_serializer="json", timezone="UTC", enable_utc=True)
celery_app.conf.beat_schedule = {
    "cleanup-expired-carts": {"task": "app.tasks.cleanup_tasks.cleanup_expired_carts", "schedule": crontab(minute="*/30")},
    "abandoned-cart-reminders": {"task": "app.tasks.abandoned_cart_tasks.send_reminders", "schedule": crontab(minute="*/15")},
    "daily-analytics": {"task": "app.tasks.analytics_tasks.daily_aggregation", "schedule": crontab(hour=2, minute=0)},
    "generate-payouts": {"task": "app.tasks.payout_tasks.generate_payouts", "schedule": crontab(hour=6, minute=0, day_of_week=1)},
    "release-expired-reservations": {"task": "app.tasks.inventory_tasks.release_expired", "schedule": crontab(minute="*/10")},
    "review-reminders": {"task": "app.tasks.review_reminder_tasks.send_review_reminders", "schedule": crontab(hour=10, minute=0)},
}
celery_app.autodiscover_tasks(["app.tasks"])
