import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_service.settings')

celery_app = Celery('email_service', broker='redis://redis:6379/0')
celery_app.config_from_object('django.conf:settings')

    

celery_app.conf.update(result_expires=3600,
                enable_utc=True,
                timezone='Europe/Moscow', )

celery_app.conf.beat_schedule = {
    "every day": {
        "task": "emailapp.tasks.sending",  
        "schedule": crontab(hour=11,
                            minute=0,
                            )}}
        
 
celery_app.autodiscover_tasks()           
