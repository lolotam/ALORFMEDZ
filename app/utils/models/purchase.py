"""
Purchase Data Model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class Purchase:
    """Purchase entity model"""
    id: str
    supplier_id: str
    medicines: List[Dict[str, any]]  # [{medicine_id, quantity, batch_number, expiry_date}]
    total_amount: float = 0.0
    status: str = "pending"  # pending, delivered, cancelled
    purchase_date: Optional[str] = None
    invoice_number: str = ""
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: dict) -> 'Purchase':
        """Create from dictionary"""
        return cls(**data)
