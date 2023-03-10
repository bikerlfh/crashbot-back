# Standard Library
from decimal import Decimal
from typing import Optional

# Django
from django.db.models import QuerySet

# Internal
from apps.django_projects.core.models import HomeBet, HomeBetMultiplier


def filter_home_bet(*, home_bet_id: Optional[int] = None) -> QuerySet[HomeBet]:
    filter_ = dict()
    if home_bet_id:
        filter_.update(id=home_bet_id)
    return HomeBet.objects.filter(**filter_).prefetch_related(
        "multipliers", "currencies"
    )


def get_last_multipliers(
    *,
    home_bet_id: int,
    count: Optional[int] = None,
    filter_: Optional[dict] = {}
) -> list[Decimal]:
    filter_.update(home_bet_id=home_bet_id)
    _multipliers = (
        HomeBetMultiplier.objects.filter(**filter_)
        .values_list("multiplier", flat=True)
        .order_by("-id")[:count]
    )
    if count is not None:
        _multipliers = _multipliers[:count]
    multipliers = list(_multipliers)
    multipliers.reverse()
    return multipliers
