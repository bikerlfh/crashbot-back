from .common import *

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


DEBUG = True

ALLOWED_HOSTS = ["*"]

THIRD_PARTY_APPS += [
    "django_extensions",
]

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS  # noqa


sentry_sdk.init(
    dsn=getenv('SENTRY_URL'),
    integrations=[DjangoIntegration()],
    environment=getenv('ENVIRONMENT', 'negligent'),
    release=getenv('RELEASE'),
    traces_sample_rate=1.0,
)
