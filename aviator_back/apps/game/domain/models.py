# Standard Library
from dataclasses import dataclass


@dataclass
class Bet:
    amount: float
    status: str
    multiplier: float | None = None
    profit_amount: float | None = None
    id: int | None = None
