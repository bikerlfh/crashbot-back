from .common import *
from os import getenv

DEBUG = False

ALLOWED_HOSTS = [
    host.strip() for host in getenv("ALLOWED_HOSTS", "").split(",")
]

CORS_ORIGIN_WHITELIST = [f"http://{host}" for host in ALLOWED_HOSTS]
CORS_ORIGIN_WHITELIST += [f"https://{host}" for host in ALLOWED_HOSTS]

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

# TODO add sentry log
# sentry_sdk.init(
#     dsn=environ.get('SENTRY_URL'),
#     integrations=[DjangoIntegration()],
#     environment=environ.get('ENVIRONMENT', 'negligent'),
#     release=environ.get('RELEASE')
# )
