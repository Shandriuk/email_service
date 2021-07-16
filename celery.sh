cd email_service
celery -A email_service worker -B --loglevel=debug --concurrency=4

