# Django
from django.db.models import QuerySet

# Internal
from apps.django_projects.customers.models import Customer, CustomerBalance


def filter_customer(
    **kwargs
) -> QuerySet[Customer]:
    return Customer.objects.filter(**kwargs)


def filter_balance(
    *,
    customer_id: int,
    home_bet_id: int | None = None
) -> QuerySet[CustomerBalance]:
    filter_ = dict(
        customer_id=customer_id
    )
    if home_bet_id is not None:
        filter_.update(
            home_bet_id=home_bet_id
        )
    return CustomerBalance.objects.filter(**filter_)
