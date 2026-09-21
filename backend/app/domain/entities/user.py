from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class User:
    id: str
    email: str
    hashed_password: str
    full_name: str
    role: str = "analyst"
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

