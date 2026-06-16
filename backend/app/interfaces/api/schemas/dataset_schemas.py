from datetime import datetime
from pydantic import BaseModel


class DatasetResponse(BaseModel):
    id: str
    filename: str
    rows: int
    columns: list[str]
    created_at: datetime


class DatasetPreviewResponse(BaseModel):
    dataset_id: str
    columns: list[str]
    rows: list[dict]
