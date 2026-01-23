"""
Store Data Model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class Store:
    """Store entity model"""
    id: str
    name: str
    department_id: str
    inventory: Dict[str, int] = field(default_factory=dict)  # {medicine_id: quantity}
    location: str = ""
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: dict) -> 'Store':
        """Create from dictionary"""
        return cls(**data)
