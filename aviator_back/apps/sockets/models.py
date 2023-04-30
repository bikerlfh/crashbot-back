# Standard Library
from dataclasses import dataclass
from typing import Optional


@dataclass
class SocketMessage:
    func: str
    message: str
    customer_id: Optional[int] = None
