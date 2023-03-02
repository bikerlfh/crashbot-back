from typing import Optional
from apps.core.models import HomeBet, HomeBetMultiplier
from decimal import Decimal


def get_home_bet_by_id(
    *,
    home_bet_id: int
) -> HomeBet:
    return HomeBet.objects.filter(
        id=home_bet_id
    ).prefetch_related("multipliers").first()


def get_last_multipliers(
    *,
    home_bet_id: int,
    count: Optional[int] = 10
) -> list[Decimal]:
    _multipliers = HomeBetMultiplier.objects.filter(
        home_bet_id=home_bet_id
    ).values_list("multiplier", flat=True).order_by("-id")[:count]
    multipliers = list(_multipliers)
    multipliers.reverse()
    return multipliers


