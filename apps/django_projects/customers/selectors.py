from typing import Optional
# Django
from django.contrib.auth.models import User
from django.db.models import QuerySet

# Internal
from apps.django_projects.customers.models import (
    Customer,
    CustomerBalance,
    CustomerPlan,
    CustomerSession
)


def filter_customer(**kwargs) -> QuerySet[Customer]:
    return Customer.objects.filter(**kwargs)


def filter_users(**kwargs) -> QuerySet[User]:
    return User.objects.filter(**kwargs)


def filter_user_by_username(*, username: str) -> QuerySet[User]:
    return filter_users(username=username)


def filter_user_by_email(*, email: str) -> QuerySet[User]:
    return filter_users(email=email)


def filter_balance(
    *, customer_id: int, home_bet_id: int | None = None
) -> QuerySet[CustomerBalance]:
    filter_ = dict(customer_id=customer_id)
    if home_bet_id is not None:
        filter_.update(home_bet_id=home_bet_id)
    return CustomerBalance.objects.filter(**filter_)


def filter_customer_plans(**kwargs) -> QuerySet[CustomerPlan]:
    return CustomerPlan.objects.filter(**kwargs)


def filter_customer_session(**kwargs) -> QuerySet[CustomerSession]:
    return CustomerSession.objects.filter(**kwargs)
