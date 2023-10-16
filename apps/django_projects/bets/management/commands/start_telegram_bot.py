# Standard Library
import logging

# Django
from django.core.management import BaseCommand

# Internal
from apps.telegram_bot import services as telegram_services

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "python manage.py start_telegram_bot"

    def handle(self, *args, **options):
        telegram_services.start_telegram_bot()
        self.stdout.write(self.style.SUCCESS("telegram bot started"))
