cd email_service
celery -A email_service worker --loglevel=debug --concurrency=4
