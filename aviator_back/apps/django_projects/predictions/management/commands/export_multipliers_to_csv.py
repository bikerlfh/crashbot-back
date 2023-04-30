# Standard Library
import logging

# Django
from django.core.management import BaseCommand

# Libraries
from apps.prediction import services

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "python manage.py export_multipliers_to_csv "

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("home_bet_id", type=int)

    def handle(self, *args, **options):
        home_bet_id = options["home_bet_id"]
        file_path = services.extract_multipliers_to_csv(
            home_bet_id=home_bet_id,
            convert_to_data=False,
        )
        self.stdout.write(self.style.SUCCESS(f"data exported to {file_path}"))
