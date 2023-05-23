from .common import *
from os import getenv

DEBUG = False

ALLOWED_HOSTS = ["*"]

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": getenv("DATABASE_NAME", "mydatabase"),
        "USER": getenv("DATABASE_USER", "mydatabaseuser"),
        "PASSWORD": getenv("DATABASE_PASSWORD", "mypassword"),
        "HOST": getenv("DATABASE_HOST", "127.0.0.1"),
        "PORT": getenv("DATABASE_PORT", "5432"),
    }
}

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS  # noqa
