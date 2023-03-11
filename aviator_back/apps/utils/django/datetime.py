from datetime import datetime
from django.utils import timezone
from django.conf import settings


def localtime(value: datetime):
    return timezone.localtime(value, settings.TIME_ZONE)
