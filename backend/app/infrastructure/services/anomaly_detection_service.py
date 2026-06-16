from typing import Any
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from app.infrastructure.services.preprocessing import DataFramePreprocessor


class SklearnAnomalyDetectionService:
    def __init__(self):
        self.preprocessor = DataFramePreprocessor()

    def run_isolation_forest(self, df: pd.DataFrame, columns: list[str] | None, contamination: float) -> dict[str, Any]:
        if not 0 < contamination < 0.5:
            raise ValueError("contamination deve estar entre 0 e 0.5")
        selected = self.preprocessor.select_features(df, columns)
        encoded = self.preprocessor.encode_for_ml(selected)
        scaled = StandardScaler().fit_transform(encoded)
        model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
        labels = model.fit_predict(scaled)
        scores = model.decision_function(scaled)
        preview = selected.copy()
        preview["anomaly"] = labels == -1
        preview["anomaly_score"] = scores
        return {
            "algorithm": "IsolationForest",
            "contamination": contamination,
            "rows_used": int(len(selected)),
            "features_used": list(selected.columns),
            "encoded_features_count": int(encoded.shape[1]),
            "anomaly_count": int((labels == -1).sum()),
            "normal_count": int((labels == 1).sum()),
            "preview": preview.sort_values("anomaly_score").head(30).fillna("").to_dict(orient="records"),
        }
