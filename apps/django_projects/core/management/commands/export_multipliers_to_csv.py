# Standard Library
import logging

# Django
from django.core.management import BaseCommand

# Internal
from apps.django_projects.core import services

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "python manage.py export_multipliers_to_csv "

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("is_production_data", type=int)

    def handle(self, *args, **options):
        is_production_data = bool(int(options["is_production_data"]))
        print("is_production_data", is_production_data)
        file_path = services.export_multipliers_to_csv(
            is_production_data=is_production_data
        )
        self.stdout.write(self.style.SUCCESS(f"data exported to {file_path}"))
