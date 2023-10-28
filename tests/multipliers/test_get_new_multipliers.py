# Libraries
# import pytest
from apps.django_projects.core.strategies.multiplier_save import (
    MultiplierSaveStrategy,
)


class TestGetNewMultipliers:
    def test_get_new_multipliers(self):
        multipliers = [
            dict(
                multiplier=1.5,
                multiplier_dt="2021-09-01 00:00:00",
            ),
            dict(
                multiplier=2,
                multiplier_dt="2021-09-01 00:00:00",
            ),
            dict(
                multiplier=2.5,
                multiplier_dt="2021-09-01 00:00:00",
            ),
            dict(
                multiplier=3,
                multiplier_dt="2021-09-01 00:00:00",
            ),
            dict(
                multiplier=3.5,
                multiplier_dt="2021-09-01 00:00:00",
            ),
            dict(
                multiplier=4,
                multiplier_dt="2021-09-01 00:00:00",
            ),
        ]
        context = MultiplierSaveStrategy(
            last_multipliers=[1.5, 2, 2.5],
            multipliers=multipliers,
        )
        new_multipliers = context.get_new_multipliers()
        new_multipliers_ = [item["multiplier"] for item in new_multipliers]
        assert new_multipliers_ == [3, 3.5, 4]

    def test_get_new_multipliers_2(self):
        multipliers = [
            dict(
                multiplier=3,
                multiplier_dt="2021-09-01 00:00:00",
            ),
            dict(
                multiplier=4,
                multiplier_dt="2021-09-01 00:00:00",
            ),
            dict(
                multiplier=5,
                multiplier_dt="2021-09-01 00:00:00",
            ),
            dict(
                multiplier=6,
                multiplier_dt="2021-09-01 00:00:00",
            ),
            dict(
                multiplier=7,
                multiplier_dt="2021-09-01 00:00:00",
            ),
            dict(
                multiplier=8,
                multiplier_dt="2021-09-01 00:00:00",
            ),
            dict(
                multiplier=8,
                multiplier_dt="2021-09-01 00:00:00",
            ),
        ]
        context = MultiplierSaveStrategy(
            last_multipliers=[1.5, 2, 2.5], multipliers=multipliers
        )
        new_multipliers = context.get_new_multipliers()
        new_multipliers_ = [item["multiplier"] for item in new_multipliers]
        assert new_multipliers_ == [3, 4, 5, 6, 7, 8, 8]

    def test_get_new_multipliers_3(self):
        multipliers = [
            {"multiplier": 3.0, "multiplier_dt": "2023-10-28 00:00:00"},
            {"multiplier": 2.4, "multiplier_dt": "2023-10-28 00:01:00"},
            {"multiplier": 1.2, "multiplier_dt": "2023-10-28 00:02:00"},
            {"multiplier": 6.2, "multiplier_dt": "2023-10-28 00:03:00"},
            {"multiplier": 1.98, "multiplier_dt": "2023-10-28 00:04:00"},
            {"multiplier": 4.5, "multiplier_dt": "2023-10-28 00:05:45"},
            {"multiplier": 5.5, "multiplier_dt": "2023-10-28 00:05:49"},
            {"multiplier": 6.5, "multiplier_dt": "2023-10-28 00:05:50"},
            {"multiplier": 7.5, "multiplier_dt": "2023-10-28 00:05:55"},
        ]
        context = MultiplierSaveStrategy(
            last_multipliers=[3.0, 2.4, 1.2, 6.2, 1.98, 4.5],
            multipliers=multipliers,
        )
        new_multipliers = context.get_new_multipliers()
        new_multipliers_ = [item["multiplier"] for item in new_multipliers]
        assert new_multipliers_ == [5.5, 6.5, 7.5]
