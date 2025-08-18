web: gunicorn app:server
worker: celery -A tools.functions_run_nma_task.celery_app worker --loglevel=info
