# Standard Library
from dataclasses import dataclass
from typing import Optional


@dataclass
class SocketMessage:
    func: str
    data: dict[str, any]


@dataclass
class UserConnection:
    channel_name: str
    unique_id: str
    allowed_to_save: bool
    customer_id: Optional[int] = None
    home_bet_id: Optional[int] = None
