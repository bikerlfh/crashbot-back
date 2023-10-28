import copy


class MultiplierSaveStrategy:
    def __init__(
        self,
        *,
        last_multipliers: list[float],
        multipliers: list[dict[str, any]]
    ):
        """
        MultiplierSaveStrategy
        :param last_multipliers: list of float with the last multipliers
        :param multipliers: list of dict with new multipliers dict(
            multiplier=multiplier,
            multiplier_dt=multiplier_dt
        )
        """
        self.last_multipliers = last_multipliers
        self.multipliers = multipliers

    def get_new_multipliers(self) -> list[dict[str, any]]:
        if not self.last_multipliers:
            return self.multipliers
        a = self.last_multipliers
        b = copy.copy(self.multipliers)
        matches = []
        i = 0
        j = 0
        while i < len(a) and j < len(b):
            multiplier_ = b[j].get("multiplier")
            if a[i] == multiplier_:
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
