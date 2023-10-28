# Standard Library
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

# Django
from django.conf import settings
from rest_framework.exceptions import ValidationError

# Internal
from apps.django_projects.core import selectors
from apps.django_projects.core.models import Multiplier
from apps.django_projects.core.strategies import multiplier_save
from cacheops import invalidate_model

logger = logging.getLogger(__name__)


def get_home_bet(
    *,
    home_bet_id: Optional[int] = None,
    game_name: Optional[str] = None,
) -> dict[str, Any] | list[dict[str, Any]]:
    home_bet_qry = selectors.filter_home_bet(
        home_bet_id=home_bet_id,
    ).prefetch_related("games")
    if not home_bet_qry.exists():
        raise ValidationError("home bet does not exists")
    data = []
    for home_bet in home_bet_qry:
        filter_ = {}
        if game_name:
            filter_.update(crash_game__name=game_name)
        print(f"filter_: {filter_}")
        games_qry = home_bet.games.filter(**filter_).values(
            "crash_game__name", "limits"
        )
        games = [
            dict(
                name=game["crash_game__name"],
                limits=game["limits"],
            )
            for game in games_qry
        ]
        data.append(
            dict(
                id=home_bet.id,
                name=home_bet.name,
                url=home_bet.url,
                games=games,
            )
        )
    return data if not home_bet_id else data[0]


def save_multipliers(
    *, home_bet_game_id: int, multipliers: list[Decimal]
) -> list[Decimal]:
    home_bet_game = selectors.filter_home_bet_game_by_id(
        home_bet_game_id=home_bet_game_id
    ).first()
    if not home_bet_game:
        raise ValidationError("Home bet game does not exists")
    last_multipliers = []
    if len(multipliers) > 1:
        last_multipliers = selectors.get_last_multipliers(
            home_bet_game_id=home_bet_game_id, count=len(multipliers)
        )
    context = multiplier_save.MultiplierSaveStrategy(
        home_bet_game=home_bet_game,
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
            Multiplier(
                home_bet_game=home_bet_game,
                multiplier=multiplier,
                multiplier_dt=now,
            )
        )
    Multiplier.objects.bulk_create(_list_multipliers)
    invalidate_model(Multiplier)
    return multipliers


def export_multipliers_to_csv(
    *, is_production_data: Optional[bool] = True
) -> str:
    # Standard Library
    import csv

    filter_ = {}
    file_name = f"multiplier_data_{datetime.now().strftime('%d%m%Y')}.csv"
    if is_production_data:
        filter_.update(home_bet_id__in=[2, 3, 4])
        file_name = f"prod_{file_name}"
    data = (
        selectors.filter_multipliers(filter_=filter_)
        .order_by("id")
        .values(
            "id",
            "created_at",
            "updated_at",
            "multiplier",
            "multiplier_dt",
            "home_bet_id",
        )
    )
    if not data:
        raise ValidationError("multipliers not found")
    file_path = f"data/{file_name}"
    with open(file_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "id",
                "created_at",
                "updated_at",
                "multiplier",
                "multiplier_dt",
                "home_bet_id",
            ]
        )
        i = 0
        for item in data:
            i += 1
            writer.writerow(
                [
                    i,
                    item["created_at"],
                    item["updated_at"],
                    item["multiplier"],
                    item["multiplier_dt"],
                    item["home_bet_id"],
                ]
            )
    return file_path


def load_data_from_csv(*, file_path: str) -> None:
    # Standard Library
    import csv

    if not settings.DEBUG:
        logger.warning("load_data_from_csv only works in debug mode")
        return
    data = []
    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(
                Multiplier(
                    id=int(row["id"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    multiplier=row["multiplier"],
                    multiplier_dt=row["multiplier_dt"],
                    home_bet_id=int(row["home_bet_id"]),
                )
            )
    batch_size = 100
    batches = [
        data[i : i + batch_size]  # noqa
        for i in range(0, len(data), batch_size)  # noqa
    ]
    for batch in batches:
        Multiplier.objects.bulk_create(
            batch, batch_size, ignore_conflicts=True
        )
        # from apps.django_projects.core.services import load_data_from_csv
        # load_data_from_csv(file_path='data/prod_multiplier_data_05062023.csv')
