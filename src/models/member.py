from dataclasses import dataclass
from typing import Optional


@dataclass
class Member:
    id: Optional[int]
    name: str
    email: str
    notes: str = ""