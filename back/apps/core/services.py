from apps.core import selectors
from rest_framework.exceptions import ValidationError
from datetime import datetime
from apps.core.models import HomeBetMultiplier
from decimal import Decimal
from apps.core.strategies import multiplier_save


def save_multipliers(
    *,
    home_bet_id: int,
    multipliers: list[Decimal]
) -> None:
    home_bet = selectors.get_home_bet_by_id(
        home_bet_id=home_bet_id
    )
    if not home_bet:
        raise ValidationError("Home bet does not exists")
    last_multipliers = []
    if len(multipliers) > 1:
        last_multipliers = selectors.get_last_multipliers(
            home_bet_id=home_bet_id,
            count=len(multipliers)
        )
    context = multiplier_save.MultiplierSaveStrategy(
        home_bet=home_bet,
        last_multipliers=last_multipliers,
        multipliers=multipliers
    )
    multipliers = context.get_new_multipliers()
    if not multipliers:
        raise ValidationError("multipliers repeated")
    now = datetime.now()
    _list_multipliers = []
    for multiplier in multipliers:
        _list_multipliers.append(HomeBetMultiplier(
            home_bet=home_bet,
            multiplier=multiplier,
            multiplier_dt=now,
        ))
    HomeBetMultiplier.objects.bulk_create(_list_multipliers)
