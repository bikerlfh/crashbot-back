# Standard Library
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

# Django
from rest_framework.exceptions import ValidationError

# Libraries
from apps.django_projects.core import selectors
from apps.django_projects.core.models import HomeBetMultiplier
from apps.django_projects.core.strategies import multiplier_save


def get_home_bet(
    *, home_bet_id: Optional[int] = None
) -> dict[str, Any] | list[dict[str, Any]]:
    home_bet_qry = selectors.filter_home_bet(home_bet_id=home_bet_id)
    if not home_bet_qry.exists():
        raise ValidationError("home bet does not exists")
    data = []
    for home_bet in home_bet_qry:
        currencies = home_bet.currencies.all().values_list("code", flat=True)
        data.append(
            dict(
                id=home_bet.id,
                name=home_bet.name,
                url=home_bet.url,
                min_bet=home_bet.min_bet,
                max_bet=home_bet.max_bet,
                count_multipliers=home_bet.multipliers.count(),
                currencies=list(currencies),
            )
        )
    return data if not home_bet_id else data[0]


def get_home_bet_multipliers(
    *, home_bet_id: int, count: Optional[int] = 10
) -> list[Decimal]:
    multipliers = selectors.get_last_multipliers(
        home_bet_id=home_bet_id, count=count
    )
    return multipliers


def save_multipliers(
    *, home_bet_id: int, multipliers: list[Decimal]
) -> list[Decimal]:
    home_bet = selectors.filter_home_bet(home_bet_id=home_bet_id).first()
    if not home_bet:
        raise ValidationError("Home bet does not exists")
    last_multipliers = []
    if len(multipliers) > 1:
        last_multipliers = selectors.get_last_multipliers(
            home_bet_id=home_bet_id, count=len(multipliers)
        )
    context = multiplier_save.MultiplierSaveStrategy(
        home_bet=home_bet,
        last_multipliers=last_multipliers,
        multipliers=multipliers,
    )
    multipliers = context.get_new_multipliers()
    if not multipliers:
        raise ValidationError("multipliers repeated")
    now = datetime.now()
    _list_multipliers = []
    for multiplier in multipliers:
        _list_multipliers.append(
            HomeBetMultiplier(
                home_bet=home_bet,
                multiplier=multiplier,
                multiplier_dt=now,
            )
        )
    HomeBetMultiplier.objects.bulk_create(_list_multipliers)
    return multipliers
