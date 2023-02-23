from django.db.models import QuerySet
from apps.core.models import HomeBet


def get_home_bet_by_id(
    *,
    home_bet_id: int
) -> HomeBet:
    return HomeBet.objects.filter(
        id=home_bet_id
    ).prefetch_related("multipliers").first()
