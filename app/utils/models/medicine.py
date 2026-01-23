"""
Medicine Data Model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Medicine:
    """Medicine entity model"""
    id: str
    name: str
    supplier_id: str
    form_dosage: str  # e.g., "Tablet 500mg"
    category: str = ""
    low_stock_limit: int = 10
    expiry_date: Optional[str] = None
    photos: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: dict) -> 'Medicine':
        """Create from dictionary"""
        return cls(**data)
