import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_service.settings')

celery_app = Celery('email_service', broker='redis://redis:6379/0')
celery_app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    'send-report-every-single-minute': {
        'task': 'publisher.tasks.sending',
        'schedule': crontab(minute=0, hour=0),  # change to `crontab(minute=0, hour=0)` if you want it to run daily at midnight
    },
}