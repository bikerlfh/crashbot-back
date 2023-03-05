from typing import Optional


class Message:
    def __init__(
        self,
        message: str,
        user: Optional[str] = None,
        silent: Optional[bool] = False
    ):
        self.message = message
        self.user = user
        self.silent = silent
