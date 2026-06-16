from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class Dataset:
    id: str
    filename: str
    stored_path: str
    rows: int
    columns: list[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
