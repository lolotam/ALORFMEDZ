"""
Transfer Data Model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class Transfer:
    """Transfer entity model"""
    id: str
    source_store_id: str
    destination_store_id: str
    medicines: List[Dict[str, any]]  # [{medicine_id, quantity}]
    status: str = "pending"  # pending, approved, rejected, completed
    transfer_date: Optional[str] = None
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: dict) -> 'Transfer':
        """Create from dictionary"""
        return cls(**data)
