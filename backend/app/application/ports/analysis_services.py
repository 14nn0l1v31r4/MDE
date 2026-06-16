from typing import Protocol, Any
import pandas as pd


class DatasetReader(Protocol):
    def read_csv(self, path: str) -> pd.DataFrame: ...


class StatisticsService(Protocol):
    def summarize(self, df: pd.DataFrame) -> dict[str, Any]: ...


class ClusteringService(Protocol):
    def run_kmeans(self, df: pd.DataFrame, columns: list[str] | None, n_clusters: int) -> dict[str, Any]: ...
    def run_dbscan(self, df: pd.DataFrame, columns: list[str] | None, eps: float, min_samples: int) -> dict[str, Any]: ...


class AnomalyDetectionService(Protocol):
    def run_isolation_forest(self, df: pd.DataFrame, columns: list[str] | None, contamination: float) -> dict[str, Any]: ...


class AssociationRulesService(Protocol):
    def mine_rules(self, df: pd.DataFrame, columns: list[str], min_support: float, min_confidence: float) -> dict[str, Any]: ...
