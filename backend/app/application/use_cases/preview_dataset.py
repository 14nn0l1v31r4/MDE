from app.application.ports.repositories import DatasetRepository
from app.application.ports.analysis_services import DatasetReader
from app.domain.exceptions.domain_exceptions import DatasetNotFoundError


class PreviewDatasetUseCase:
    def __init__(self, repository: DatasetRepository, reader: DatasetReader):
        self.repository = repository
        self.reader = reader

    def execute(self, dataset_id: str, limit: int = 10) -> dict:
        dataset = self.repository.get_by_id(dataset_id)
        if dataset is None:
            raise DatasetNotFoundError(f"Dataset {dataset_id} não encontrado")
        df = self.reader.read_csv(dataset.stored_path)
        return {
            "dataset_id": dataset_id,
            "columns": [str(column) for column in df.columns],
            "rows": df.head(limit).fillna("").to_dict(orient="records"),
        }
