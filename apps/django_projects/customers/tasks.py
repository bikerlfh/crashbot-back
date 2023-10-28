# Libraries
from celery import shared_task
from celery.utils.log import get_task_logger

# Internal
from apps.django_projects.customers import services

logger = get_task_logger(__name__)


@shared_task
def task_inactive_customer_plans_at_end_dt():
    services.inactive_customer_plans_at_end_dt()
    logger.info("task_inactive_customer_plans_at_end_dt invoked")


@shared_task
def task_inactive_customer_sessions():
    services.inactive_customer_sessions()
    logger.info("task_inactive_customer_sessions invoked")
