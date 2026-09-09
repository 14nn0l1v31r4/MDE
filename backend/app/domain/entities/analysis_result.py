from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class AnalysisResult:
    id: str
    dataset_id: str
    analysis_type: str
    payload: dict[str, Any]
    user_id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
