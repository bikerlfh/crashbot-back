import functools
from decimal import Decimal
from rest_framework.exceptions import ValidationError
from apps.core.models import HomeBet


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
        self,
        *,
        last_multipliers: list[Decimal],
        multipliers: list[Decimal]
    ) -> bool:
        return functools.reduce(
            lambda x, y: x and y, map(
                lambda p, q: p == q, last_multipliers, multipliers
            ), True
        )

    def get_new_multipliers(self) -> list[Decimal]:
        if not self.last_multipliers or \
                len(self.last_multipliers) != len(self.multipliers):
            return self.multipliers
        len_index = len(self.multipliers) - 1
        index = 0
        index_2 = 5
        exist = False
        while index < len_index - 5:
            i = 0
            while i <= len_index:
                i_2 = i + 5
                if i_2 > len_index:
                    i_2 = len_index
                is_same = self._compare_multipliers(
                    last_multipliers=self.last_multipliers[index: index_2],
                    multipliers=self.multipliers[i:i_2]
                )
                if is_same:
                    exist = True
                    i += 5
                    index += 5
                    index_2 += 5
                    if index_2 > len_index:
                        index_2 = len_index
                    continue
                elif exist:
                    return self.multipliers[i:]
                i += 1
        if exist:
            return []
        return self.multipliers

