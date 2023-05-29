from .common import *


DEBUG = True

ALLOWED_HOSTS = ["*"]

THIRD_PARTY_APPS += [
    "django_extensions",
]

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS  # noqa
