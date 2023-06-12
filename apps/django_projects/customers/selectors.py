# Django
from django.db.models import QuerySet
from django.contrib.auth.models import User

# Internal
from apps.django_projects.customers.models import Customer, CustomerBalance


def filter_customer(**kwargs) -> QuerySet[Customer]:
    return Customer.objects.filter(**kwargs)


def filter_user_by_username(*, username: str) -> QuerySet[User]:
    return User.objects.filter(username=username)


def filter_user_by_email(*, email: str) -> QuerySet[User]:
    return User.objects.filter(email=email)


def filter_balance(
    *, customer_id: int, home_bet_id: int | None = None
) -> QuerySet[CustomerBalance]:
    filter_ = dict(customer_id=customer_id)
    if home_bet_id is not None:
        filter_.update(home_bet_id=home_bet_id)
    return CustomerBalance.objects.filter(**filter_)
