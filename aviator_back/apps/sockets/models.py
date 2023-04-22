from typing import Optional
from dataclasses import dataclass


@dataclass
class SocketMessage:
    func: str
    message: str
    customer_id: Optional[int] = None
