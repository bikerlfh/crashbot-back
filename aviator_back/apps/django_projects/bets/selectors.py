from django.db.models import QuerySet

from apps.django_projects.bets.models import (
    Customer, CustomerBalance, Bet
)


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


def filter_customer_bets(
    *,
    customer_id: int,
    home_bet_id: int,
    status: str | None = None
) -> QuerySet[Bet]:
    filter_ = dict(
        balance__customer_id=customer_id,
        balance__home_bet_id=home_bet_id
    )
    if status is not None:
        filter_.update(status=status)
    return Bet.objects.filter(**filter_)


def filter_bet(
    **kwargs
) -> QuerySet[Bet]:
    return Bet.objects.filter(**kwargs)
