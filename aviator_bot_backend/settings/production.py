from .common import *
from os import getenv

DEBUG = True

ALLOWED_HOSTS = ["*"]

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
