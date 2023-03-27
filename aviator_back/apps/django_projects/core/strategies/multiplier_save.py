# Standard Library
import functools
from decimal import Decimal

# Django
from rest_framework.exceptions import ValidationError

# Internal
from apps.django_projects.core.models import HomeBet


class MultiplierSaveStrategy:
    def __init__(
        self,
        *,
        home_bet: HomeBet,
        last_multipliers: list[Decimal],
        multipliers: list[Decimal]
    ):
        self.home_bet = home_bet
        self.last_multipliers = last_multipliers
        self.multipliers = multipliers

    def is_valid(self):
        if self.home_bet is None:
            raise ValidationError("home bet does not exists")
        if not self.multipliers:
            raise ValidationError("multipliers required")

    def _compare_multipliers(
        self, *, last_multipliers: list[Decimal], multipliers: list[Decimal]
    ) -> bool:
        return functools.reduce(
            lambda x, y: x and y,
            map(lambda p, q: p == q, last_multipliers, multipliers),
            True,
        )

    def get_new_multipliers(self) -> list[Decimal]:
        if not self.last_multipliers:
            return self.multipliers
        a = self.last_multipliers
        b = self.multipliers
        matches = []
        i = 0
        j = 0
        while i < len(a) and j < len(b):
            if a[i] == b[j]:
                matches.append(a[i])
                i += 1
                j += 1
                continue
            i += 1
            len_matches = len(matches)
            if 3 <= len_matches == a.index(matches[-1]):
                break
            matches = []
        if len(matches) > 0:
            return b[j:]
        return b
