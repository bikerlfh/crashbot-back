# Standard Library
import logging

# Django
from django.core.management import BaseCommand

# Internal
from apps.django_projects.predictions import services
from apps.prediction.constants import ModelType

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "python manage.py create_sequential_model"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("home_bet_id", type=int)
        parser.add_argument(
            "model_type",
            type=str,
            help="model type (sequential, sequential_lstm)"
        )
        parser.add_argument(
            "seq_len",
            type=int,
            nargs='?',
            help="size of sequential"
        )

    def handle(self, *args, **options):
        home_bet_id = options["home_bet_id"]
        seq_len = options["seq_len"] or 15
        model_type = ModelType(options["model_type"])
        model_home_bet = services.create_model_with_all_multipliers(
            home_bet_id=home_bet_id,
            seq_len=seq_len,
            model_type=model_type,
        )
        self.stdout.write(
            self.style.SUCCESS(f"model home bet {model_home_bet.id} created")
        )
