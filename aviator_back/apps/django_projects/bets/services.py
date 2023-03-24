# Django
from rest_framework.exceptions import ValidationError

# Internal
from apps.django_projects.bets import selectors
from apps.django_projects.bets.constants import BetStatus
from apps.django_projects.bets.models import Bet
from apps.django_projects.customers import selectors as customer_selectors


def create_bet(
    *,
    external_id: str,
    customer_id: int,
    home_bet_id: int,
    prediction: float,
    amount: float,
    multiplier: float,
    multiplier_result: float,
) -> Bet:
    balance = customer_selectors.filter_balance(
        customer_id=customer_id, home_bet_id=home_bet_id
    ).first()
    if not balance:
        raise ValidationError("Balance does not exist")

    bet_exists = selectors.filter_bet(
        external_id=external_id,
        balance__customer_id=customer_id,
    ).exists()
    if bet_exists:
        raise ValidationError("Bet already exists")
    profit_amount = amount * (multiplier - 1)
    status = BetStatus.WON.value
    if multiplier >= multiplier_result:
        profit_amount = -amount
        status = BetStatus.LOST.value
    bet = Bet.objects.create(
        balance_id=balance.id,
        external_id=external_id,
        prediction=prediction,
        amount=amount,
        multiplier=multiplier,
        multiplier_result=multiplier_result,
        profit_amount=profit_amount,
        status=status,
    )
    return bet


def get_bet(*, bet_id: int) -> dict[str, any]:
    bet_data = (
        selectors.filter_bet(id=bet_id)
        .values(
            "id",
            "prediction",
            "prediction_round",
            "amount",
            "multiplier",
            "multiplier_result",
            "profit_amount",
            "status",
        )
        .first()
    )
    if not bet_data:
        raise ValidationError("Bet does not exist")
    return bet_data
