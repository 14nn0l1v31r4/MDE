from typing import Any
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from app.infrastructure.services.preprocessing import DataFramePreprocessor


class SklearnClusteringService:
    def __init__(self):
        self.preprocessor = DataFramePreprocessor()

    def _prepare(self, df: pd.DataFrame, columns: list[str] | None):
        selected = self.preprocessor.select_features(df, columns)
        encoded = self.preprocessor.encode_for_ml(selected)
        scaled = StandardScaler().fit_transform(encoded)
        return selected, encoded, scaled

    def run_kmeans(self, df: pd.DataFrame, columns: list[str] | None, n_clusters: int) -> dict[str, Any]:
        if n_clusters < 2:
            raise ValueError("n_clusters deve ser maior ou igual a 2")
        selected, encoded, scaled = self._prepare(df, columns)
        model = KMeans(n_clusters=n_clusters, random_state=61658, n_init=10, max_iter=10_000)
        labels = model.fit_predict(scaled)
        counts = pd.Series(labels).value_counts().sort_index().astype(int).to_dict()
        preview = selected.copy()
        preview["cluster"] = labels
        return {
            "algorithm": "KMeans",
            "n_clusters": n_clusters,
            "rows_used": int(len(selected)),
            "features_used": list(selected.columns),
            "encoded_features_count": int(encoded.shape[1]),
            "inertia": float(model.inertia_),
            "cluster_counts": {str(k): int(v) for k, v in counts.items()},
            "cluster_percentages": self._cluster_percentages(labels),
            "elbow_curve": self._build_elbow_curve(scaled),
            "cluster_profiles": self._build_cluster_profiles(selected, labels),
            "preview": preview.head(30).fillna("").to_dict(orient="records"),
        }

    def run_dbscan(self, df: pd.DataFrame, columns: list[str] | None, eps: float, min_samples: int) -> dict[str, Any]:
        selected, encoded, scaled = self._prepare(df, columns)
        model = DBSCAN(eps=eps, min_samples=min_samples)
        labels = model.fit_predict(scaled)
        counts = pd.Series(labels).value_counts().sort_index().astype(int).to_dict()
        preview = selected.copy()
        preview["cluster"] = labels
        return {
            "algorithm": "DBSCAN",
            "eps": eps,
            "min_samples": min_samples,
            "rows_used": int(len(selected)),
            "features_used": list(selected.columns),
            "encoded_features_count": int(encoded.shape[1]),
            "cluster_counts": {str(k): int(v) for k, v in counts.items()},
            "cluster_percentages": self._cluster_percentages(labels),
            "noise_count": int((labels == -1).sum()),
            "cluster_profiles": self._build_cluster_profiles(selected, labels),
            "preview": preview.head(30).fillna("").to_dict(orient="records"),
        }

    def _cluster_percentages(self, labels) -> dict[str, float]:
        counts = pd.Series(labels).value_counts().sort_index()
        total = counts.sum()
        return {str(k): float((v / total) * 100) if total else 0.0 for k, v in counts.items()}

    def _build_elbow_curve(self, scaled) -> list[dict[str, Any]]:
        n_samples = len(scaled)
        if n_samples < 3:
            return []
        max_clusters = min(14, n_samples - 1)
        points: list[dict[str, Any]] = []
        for k in range(2, max_clusters + 1):
            model = KMeans(n_clusters=k, max_iter=10_000, n_init=10, random_state=61658)
            model.fit(scaled)
            points.append({"n_clusters": int(k), "distortion": float(model.inertia_)})
        return points

    def _build_cluster_profiles(self, selected: pd.DataFrame, labels) -> list[dict[str, Any]]:
        profile_df = selected.copy()
        profile_df["cluster"] = labels
        clusters = sorted(profile_df["cluster"].dropna().unique().tolist())
        profiles: list[dict[str, Any]] = []

        for column in selected.columns[:30]:
            if pd.api.types.is_numeric_dtype(selected[column]):
                values = []
                for cluster in clusters:
                    subset = profile_df.loc[profile_df["cluster"] == cluster, column]
                    values.append({
                        "cluster": str(cluster),
                        "label": str(column),
                        "value": float(subset.mean()) if len(subset) else 0.0,
                        "metric": "mean",
                    })
                values.append({
                    "cluster": "All",
                    "label": str(column),
                    "value": float(selected[column].mean()) if len(selected[column]) else 0.0,
                    "metric": "mean",
                })
                profiles.append({
                    "column": str(column),
                    "type": "numeric",
                    "title": f"Média de {column} por cluster",
                    "values": values,
                })
            else:
                values = []
                for cluster in clusters:
                    subset = profile_df.loc[profile_df["cluster"] == cluster, column].fillna("Não informado").astype(str)
                    total = len(subset)
                    for category, count in subset.value_counts().head(8).items():
                        values.append({
                            "cluster": str(cluster),
                            "label": str(category),
                            "value": float((count / total) * 100) if total else 0.0,
                            "metric": "percentage",
                        })
                all_series = selected[column].fillna("Não informado").astype(str)
                total = len(all_series)
                for category, count in all_series.value_counts().head(8).items():
                    values.append({
                        "cluster": "All",
                        "label": str(category),
                        "value": float((count / total) * 100) if total else 0.0,
                        "metric": "percentage",
                    })
                profiles.append({
                    "column": str(column),
                    "type": "categorical",
                    "title": f"Perfil de {column} por cluster",
                    "values": values,
                })

        return profiles
