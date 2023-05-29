# Standard Library
import os

# Libraries
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aviator_bot_backend.settings")

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
