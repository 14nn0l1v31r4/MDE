import pandas as pd


class PandasDatasetReader:
    def read_csv(self, path: str) -> pd.DataFrame:
        encodings = ["utf-8", "latin-1", "cp1252"]
        last_error: Exception | None = None
        for encoding in encodings:
            try:
                return pd.read_csv(path, encoding=encoding)
            except Exception as error:
                last_error = error
        raise ValueError(f"Não foi possível ler o CSV: {last_error}")
