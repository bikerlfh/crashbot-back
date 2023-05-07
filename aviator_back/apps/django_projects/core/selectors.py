# Standard Library
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

# Django
from django.db.models import Q, QuerySet

# Internal
from apps.django_projects.core.models import HomeBet, HomeBetMultiplier


def filter_home_bet(
    *,
    home_bet_id: Optional[int] = None,
    filter_: Optional[dict] = None,
) -> QuerySet[HomeBet]:
    filter_ = filter_ or {}
    if home_bet_id:
        filter_.update(id=home_bet_id)
    return HomeBet.objects.filter(**filter_).prefetch_related(
        "multipliers", "currencies"
    )


def filter_home_bet_in_play() -> QuerySet[HomeBet]:
    now = datetime.now() - timedelta(minutes=10)
    return HomeBet.objects.filter(
        Q(models__isnull=True) | Q(multipliers__multiplier_dt__gte=now),
        multipliers__isnull=False,
    ).distinct("id")


def get_last_multipliers(
    *,
    home_bet_id: int,
    count: Optional[int] = None,
    filter_: Optional[dict] = {},
) -> list[Decimal]:
    filter_.update(home_bet_id=home_bet_id)
    _multipliers = (
        HomeBetMultiplier.objects.filter(**filter_)
        .values_list("multiplier", flat=True)
        .order_by("-id")[:count]
    )
    multipliers = list(_multipliers)
    multipliers.reverse()
    return multipliers


def get_today_multipliers(*, home_bet_id: int) -> list[Decimal]:
    now = datetime.now().date()
    filter_ = dict(
        home_bet_id=home_bet_id,
        multiplier_dt__date=now,
    )
    _multipliers = (
        HomeBetMultiplier.objects.filter(**filter_)
        .values_list("multiplier", flat=True)
        .order_by("-id")
    )
    multipliers = list(_multipliers)
    multipliers.reverse()
    return multipliers


def count_home_bet_multipliers(
    *, home_bet_id: int, only_today: Optional[bool] = False
) -> int:
    filter_ = dict(
        home_bet_id=home_bet_id,
    )
    if only_today:
        now = datetime.now().date()
        filter_.update(multiplier_dt__date=now)
    return HomeBetMultiplier.objects.filter(**filter_).count()
