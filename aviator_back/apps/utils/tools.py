# Standard Library
from enum import Enum
from typing import Any


def enum_to_choices(obj: type[Enum]) -> list[tuple[Any, str]]:
    return [(elem.value, elem.name) for elem in iter(obj)]  # type: ignore
