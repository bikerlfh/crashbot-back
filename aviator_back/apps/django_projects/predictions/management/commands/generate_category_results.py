# Standard Library
import logging
from decimal import Decimal
from apps.django_projects.predictions import services
from apps.prediction.constants import ModelType

# Django
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "python manage.py generate_category_results"

    def handle(self, *args, **options):
        services.generate_category_results_of_models()
        self.stdout.write(
            self.style.SUCCESS("generate_category_results successfully")
        )
