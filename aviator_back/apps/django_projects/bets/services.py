from rest_framework.exceptions import ValidationError
from apps.django_projects.bets import selectors
from apps.django_projects.bets.constants import BetStatus
from apps.django_projects.bets.models import CustomerBalance, Bet
from apps.django_projects.core import selectors as core_selectors


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
        username=balance.username,
        password=balance.get_password(),
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


def create_bet(
    *,
    customer_id: int,
    home_bet_id: int,
    amount: float,
    multiplier: float | None = None,
    profit_amount: float,
    status: str
) -> Bet:
    balance = selectors.filter_balance(
        customer_id=customer_id,
        home_bet_id=home_bet_id
    ).first()
    if not balance:
        raise ValidationError("Balance does not exist")
    bet = Bet.objects.create(
        balance_id=balance.balance_id,
        amount=amount,
        multiplier=multiplier,
        profit_amount=profit_amount,
        status=status
    )
    return bet


def process_bet(
    *,
    bet_id: int,
    multiplier: float
) -> None:
    bet = selectors.filter_bet(id=bet_id).first()
    if not bet:
        raise ValidationError("Bet does not exist")
    bet.status = BetStatus.WON.value
    if bet.multiplier > multiplier:
        bet.status = BetStatus.LOST.value
    bet.save()
