# Standard Library
import logging

# Libraries
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Current Folder
from .common import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

THIRD_PARTY_APPS += [
    "django_extensions",
]

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS  # noqa


sentry_logging = LoggingIntegration(
    level=logging.INFO, event_level=logging.WARNING
)

sentry_sdk.init(
    dsn=getenv("SENTRY_URL"),
    integrations=[sentry_logging, DjangoIntegration(), CeleryIntegration()],
    environment=getenv("ENVIRONMENT", "negligent"),
    release=getenv("RELEASE"),
    traces_sample_rate=1.0,
)
