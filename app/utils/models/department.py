"""
Department Data Model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Department:
    """Department entity model"""
    id: str
    name: str
    description: str = ""
    responsible_person: str = ""
    telephone: str = ""
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: dict) -> 'Department':
        """Create from dictionary"""
        return cls(**data)
