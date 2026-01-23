"""
User Data Model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User entity model"""
    id: str
    username: str
    password: str  # Hashed password
    role: str  # 'admin' or 'department_user'
    name: str
    email: str
    department_id: Optional[str] = None
    failed_login_attempts: int = 0
    account_locked: bool = False
    password_changed_at: Optional[str] = None
    must_change_password: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create from dictionary"""
        return cls(**data)
