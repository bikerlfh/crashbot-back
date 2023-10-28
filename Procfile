web: gunicorn --bind 127.0.0.1:8000 --workers=1 --threads=15 aviator_bot_backend.wsgi:application
# websocket: daphne -b 127.0.0.1 -p 8001 aviator_bot_backend.asgi:application
celery-worker: celery -A aviator_bot_backend.celery worker -l info
celery-beat: celery -A aviator_bot_backend.celery beat -l info