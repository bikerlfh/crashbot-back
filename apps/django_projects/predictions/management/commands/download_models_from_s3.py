# Standard Library
import logging

# Django
from django.core.management import BaseCommand

# Internal
from apps.django_projects.predictions import services

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "python manage.py download_models_from_s3"

    def handle(self, *args, **options):
        services.download_models_from_s3()
        self.stdout.write(self.style.SUCCESS("download_models_from_s3 successfully"))
