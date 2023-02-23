from apps.core import selectors
from rest_framework.exceptions import ValidationError
from datetime import datetime
from apps.core.models import HomeBetMultiplier


def save_game_results(
    *,
    home_bet_id: int,
    list_multipliers: list[dict]
) -> None:
    home_bet = selectors.get_home_bet_by_id(
        home_bet_id=home_bet_id
    )
    if not home_bet:
        raise ValidationError("Home bet does not exists")
    now = datetime.now()
    _list_multipliers = []
    for multiplier in list_multipliers:
        _list_multipliers.append(HomeBetMultiplier(
            home_bet=home_bet,
            multiplier=multiplier["multiplier"],
            number_of_players=multiplier.get("number_of_players", 0),
            multiplier_dt=multiplier.get("multiplier_dt", now),
        ))
    HomeBetMultiplier.objects.bulk_create(_list_multipliers)
