import pandas as pd


class DataFramePreprocessor:
    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        normalized = df.copy()
        normalized.columns = (
            normalized.columns.astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_", regex=False)
        )
        return normalized

    def select_features(self, df: pd.DataFrame, columns: list[str] | None) -> pd.DataFrame:
        work = self.normalize_columns(df)
        normalized_columns = [column.strip().lower().replace(" ", "_") for column in columns] if columns else list(work.columns)
        missing = [column for column in normalized_columns if column not in work.columns]
        if missing:
            raise ValueError(f"Colunas não encontradas: {missing}")
        return work[normalized_columns].dropna()

    def encode_for_ml(self, df: pd.DataFrame) -> pd.DataFrame:
        # Reproduz a ideia dos notebooks: transformar atributos categóricos em dummies
        # e manter atributos numéricos para algoritmos do scikit-learn.
        return pd.get_dummies(df, drop_first=False).astype(float)
