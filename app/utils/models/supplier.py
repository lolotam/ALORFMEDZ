"""
Supplier Data Model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Supplier:
    """Supplier entity model"""
    id: str
    name: str
    contact_person: str = ""
    email: str = ""
    telephone: str = ""
    address: str = ""
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: dict) -> 'Supplier':
        """Create from dictionary"""
        return cls(**data)
