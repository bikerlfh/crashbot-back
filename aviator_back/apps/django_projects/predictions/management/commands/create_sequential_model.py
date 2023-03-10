# Standard Library
import logging
from decimal import Decimal
from apps.django_projects.predictions import services
from apps.prediction.constants import ModelType

# Django
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "python manage.py create_sequential_model"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("home_bet_id", type=int)
        parser.add_argument("length_window", type=int)

    def handle(self, *args, **options):
        home_bet_id = options["home_bet_id"]
        length_window = options["length_window"]
        model_home_bet = services.create_model_with_all_multipliers(
            home_bet_id=home_bet_id,
            length_window=length_window,
            model_type=ModelType.SEQUENTIAL,
        )
        self.stdout.write(
            self.style.SUCCESS(f"model home bet {model_home_bet.id} created")
        )
