from typing import Any
from pydantic import BaseModel, Field


class DatasetAnalysisRequest(BaseModel):
    dataset_id: str


class KMeansRequest(DatasetAnalysisRequest):
    columns: list[str] | None = None
    n_clusters: int = Field(default=3, ge=2, le=20)


class DBSCANRequest(DatasetAnalysisRequest):
    columns: list[str] | None = None
    eps: float = Field(default=1.5, gt=0)
    min_samples: int = Field(default=5, ge=2)


class IsolationForestRequest(DatasetAnalysisRequest):
    columns: list[str] | None = None
    contamination: float = Field(default=0.05, gt=0, lt=0.5)


class AssociationRulesRequest(DatasetAnalysisRequest):
    columns: list[str]
    min_support: float = Field(default=0.2, gt=0, le=1)
    min_confidence: float = Field(default=0.6, gt=0, le=1)


class AnalysisResultResponse(BaseModel):
    id: str
    dataset_id: str
    analysis_type: str
    payload: dict[str, Any]
