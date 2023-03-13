# Django
from rest_framework.exceptions import ValidationError

# Internal
from apps.django_projects.core import selectors as core_selectors
from apps.django_projects.customers import selectors
from apps.django_projects.customers.models import CustomerBalance


def create_customer_balance(
    *,
    customer_id: int,
    home_bet_id: int,
    currency_id: int,
    amount: float,
    username: str | None = None,
    password: str | None = None,
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
        username=username,
        password=password,
        currency_id=currency_id,
        amount=amount
    )
    return balance


def get_customer_balance_data(
    *,
    customer_id: int,
    home_bet_id: int
) -> dict[str, any]:
    balance = selectors.filter_balance(
        customer_id=customer_id,
        home_bet_id=home_bet_id
    ).first()
    if not balance:
        raise ValidationError("Balance does not exist")
    data = dict(
        amount=balance.amount,
        # username=balance.username,
        # password=balance.get_password(),
    )
    return data


def update_customer_balance(
    *,
    customer_id: int,
    home_bet_id: int,
    amount: float,
    username: str | None = None,
    password: str | None = None,
) -> CustomerBalance:
    balance = selectors.filter_balance(
        customer_id=customer_id,
        home_bet_id=home_bet_id
    ).first()
    if not balance:
        raise ValidationError("Balance does not exist")
    balance.amount = amount
    if username is not None:
        balance.username = username
    if password is not None:
        balance.password = password
    balance.save()
    return balance
