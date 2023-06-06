from .common import *
from os import getenv

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
STORAGES = {"staticfiles": {"BACKEND": "storages.backends.s3boto3.S3StaticStorage", "OPTIONS": {"location": "static"}}}

AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = getenv("AWS_STORAGE_BUCKET_NAME")


# TODO add sentry log
# sentry_sdk.init(
#     dsn=environ.get('SENTRY_URL'),
#     integrations=[DjangoIntegration()],
#     environment=environ.get('ENVIRONMENT', 'negligent'),
#     release=environ.get('RELEASE')
# )
