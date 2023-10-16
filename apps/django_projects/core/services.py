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
from apps.django_projects.core.models import HomeBetMultiplier
from apps.django_projects.core.strategies import multiplier_save

logger = logging.getLogger(__name__)


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
                HomeBetMultiplier(
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
        HomeBetMultiplier.objects.bulk_create(
            batch, batch_size, ignore_conflicts=True
        )
        # from apps.django_projects.core.services import load_data_from_csv
        # load_data_from_csv(file_path='data/prod_multiplier_data_05062023.csv')
