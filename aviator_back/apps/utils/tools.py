from typing import Any
from enum import Enum


def enum_to_choices(obj: type[Enum]) -> list[tuple[Any, str]]:
    return [(elem.value, elem.name) for elem in iter(obj)]  # type: ignore
