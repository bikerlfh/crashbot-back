from .common import *
from os import getenv

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = False

ALLOWED_HOSTS = [
    host.strip() for host in getenv("ALLOWED_HOSTS", "").split(",")
]

# CORS_ORIGIN_WHITELIST = [f"http://{host}" for host in ALLOWED_HOSTS]
# CORS_ORIGIN_WHITELIST += [f"https://{host}" for host in ALLOWED_HOSTS]
# CORS_ORIGIN_WHITELIST += [f"ws://{host}" for host in ALLOWED_HOSTS]
# CORS_ORIGIN_WHITELIST += [f"wss://{host}" for host in ALLOWED_HOSTS]

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": getenv("RDS_DB_NAME"),
        "USER": getenv("RDS_USERNAME"),
        "PASSWORD": getenv("RDS_PASSWORD"),
        "HOST": getenv("RDS_HOSTNAME"),
        "PORT": getenv("RDS_PORT"),
    }
}

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS  # noqa

# static files
STORAGES = {"staticfiles": {"BACKEND": "aviator_bot_backend.custom_storage.StaticStorage"}}

AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = getenv("AWS_STORAGE_BUCKET_NAME")


sentry_sdk.init(
    dsn=getenv('SENTRY_URL'),
    integrations=[DjangoIntegration()],
    environment=getenv('ENVIRONMENT', 'negligent'),
    release=getenv('RELEASE'),
    traces_sample_rate=1.0,
)
