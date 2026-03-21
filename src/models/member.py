from dataclasses import dataclass
from typing import Optional


@dataclass
class Member:
    id: Optional[int]
    first_name: str
    last_name: str
    email: str
    notes: str = ""

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()