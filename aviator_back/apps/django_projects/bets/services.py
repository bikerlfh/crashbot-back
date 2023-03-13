from rest_framework.exceptions import ValidationError
from apps.django_projects.bets import selectors
from apps.django_projects.bets.constants import BetStatus
from apps.django_projects.bets.models import Bet
from apps.django_projects.customers import selectors as customer_selectors


def create_bet(
    *,
    customer_id: int,
    home_bet_id: int,
    prediction: float,
    prediction_round: int,
    amount: float,
    multiplier: float,
) -> Bet:
    balance = customer_selectors.filter_balance(
        customer_id=customer_id,
        home_bet_id=home_bet_id
    ).first()
    if not balance:
        raise ValidationError("Balance does not exist")
    bet = Bet.objects.create(
        balance_id=balance.id,
        prediction=prediction,
        prediction_round=prediction_round,
        amount=amount,
        multiplier=multiplier,
        status=BetStatus.PENDING.value
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
    bet.multiplier_result = multiplier
    if bet.multiplier <= multiplier:
        bet.status = BetStatus.WON.value
        bet.profit_amount = bet.amount * (bet.multiplier - 1)
    else:
        bet.status = BetStatus.LOST.value
        bet.profit_amount = -bet.amount
    bet.save()
