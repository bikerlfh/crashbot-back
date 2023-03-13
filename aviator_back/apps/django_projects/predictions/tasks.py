# Libraries
from celery import shared_task
from celery.utils.log import get_task_logger

# Internal
from apps.django_projects.predictions import services

logger = get_task_logger(__name__)


@shared_task
def task_generate_category_result():
    services.generate_category_results_of_models()
    logger.info("task_generate_category_result successfully")


@shared_task
def task_create_sequential_models():
    """
    create sequential models for all home bets
    """
    services.create_model_for_all_in_play_home_bet()
    logger.info("task_create_sequential_model successfully")
