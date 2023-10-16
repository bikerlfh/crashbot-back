# Standard Library
import logging

# Django
from django.core.management import BaseCommand

# Internal
from apps.django_projects.predictions import services

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "python manage.py generate_category_results"

    def handle(self, *args, **options):
        services.generate_category_results_of_models()
        self.stdout.write(
            self.style.SUCCESS("generate_category_results successfully")
        )
