# Standard Library
from datetime import datetime

# Django
from django.conf import settings
from django.utils import timezone


def localtime(value: datetime):
    return timezone.localtime(value, settings.TIME_ZONE)
