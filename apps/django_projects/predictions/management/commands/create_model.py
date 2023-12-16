# Standard Library
import logging

# Django
from django.core.management import BaseCommand

# Internal
from apps.django_projects.predictions import services
from apps.django_projects.predictions.constants import DEFAULT_SEQ_LEN
from apps.prediction.constants import ModelType

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "python manage.py create_model home_bet_game_id model_type seq_len"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("home_bet_game_id", type=int)
        parser.add_argument(
            "model_type",
            type=str,
            nargs="?",
            help="model type (sequential, sequential_lstm, transformer)",
        )
        parser.add_argument(
            "seq_len", type=int, nargs="?", help="size of sequential"
        )

    def handle(self, *args, **options):
        home_bet_game_id = options["home_bet_game_id"]
        seq_len = options["seq_len"] or DEFAULT_SEQ_LEN
        model_type_ = options["model_type"] or ModelType.SEQUENTIAL_LSTM.value
        model_type = ModelType(model_type_)
        model_home_bet = services.generate_model(
            home_bet_game_id=home_bet_game_id,
            seq_len=seq_len,
            model_type=model_type,
        )
        self.stdout.write(
            self.style.SUCCESS(f"model home bet {model_home_bet.id} created")
        )
