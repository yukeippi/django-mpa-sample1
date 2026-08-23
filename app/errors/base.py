from dataclasses import dataclass, field
from typing import Any


@dataclass(eq=False)
class DomainError(Exception):
    code: str
    params: dict[str, Any] = field(default_factory=dict)
