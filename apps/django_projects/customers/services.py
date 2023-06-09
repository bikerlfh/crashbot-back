# Standard Library
import logging

# Django
from rest_framework.exceptions import ValidationError

# Internal
from apps.django_projects.core import selectors as core_selectors
from apps.django_projects.customers import selectors
from apps.django_projects.customers.models import CustomerBalance

logger = logging.getLogger(__name__)


def get_customer_data(*, user_id: int) -> dict[str, any]:
    customer = (
        selectors.filter_customer(user_id=user_id)
        .prefetch_related("balances", "balances__home_bet")
        .first()
    )
    if not customer:
        raise ValidationError("Customer does not exist")
    # TODO add more data if required
    home_bets = []
    for balance in customer.balances.all().order_by("home_bet__id"):
        home_bet = balance.home_bet
        home_bets.append(
            dict(
                id=home_bet.id,
                name=home_bet.name,
                url=home_bet.url,
                min_bet=home_bet.min_bet,
                max_bet=home_bet.max_bet,
            )
        )
    data = dict(customer_id=customer.id, home_bets=home_bets)
    return data


def create_customer_balance(
    *,
    customer_id: int,
    home_bet_id: int,
    amount: float,
) -> CustomerBalance:
    customer = selectors.filter_customer(id=customer_id).first()
    if not customer:
        raise ValidationError("Customer does not exist")
    home_bet = core_selectors.filter_home_bet(home_bet_id=home_bet_id).first()
    if not home_bet:
        raise ValidationError("Home bet does not exist")
    balance = CustomerBalance.objects.create(
        customer_id=customer_id,
        home_bet_id=home_bet_id,
        amount=amount,
    )
    return balance


def get_customer_balance_data(*, customer_id: int, home_bet_id: int) -> dict[str, any]:
    balance = selectors.filter_balance(
        customer_id=customer_id, home_bet_id=home_bet_id
    ).first()
    if not balance:
        raise ValidationError("Balance does not exist")
    data = dict(amount=balance.amount)
    return data


def update_customer_balance(
    *,
    customer_id: int,
    home_bet_id: int,
    amount: float,
) -> CustomerBalance:
    balance = selectors.filter_balance(
        customer_id=customer_id, home_bet_id=home_bet_id
    ).first()
    if not balance:
        raise ValidationError("Balance does not exist")
    balance.amount = amount
    balance.save()
    return balance
