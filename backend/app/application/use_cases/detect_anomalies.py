from uuid import uuid4
from app.application.ports.repositories import DatasetRepository, AnalysisResultRepository
from app.application.ports.analysis_services import DatasetReader, AnomalyDetectionService
from app.domain.entities.analysis_result import AnalysisResult
from app.domain.exceptions.domain_exceptions import DatasetNotFoundError


class DetectAnomaliesUseCase:
    def __init__(self, datasets: DatasetRepository, results: AnalysisResultRepository, reader: DatasetReader, service: AnomalyDetectionService):
        self.datasets = datasets
        self.results = results
        self.reader = reader
        self.service = service

    def execute(self, dataset_id: str, columns: list[str] | None, contamination: float) -> AnalysisResult:
        dataset = self.datasets.get_by_id(dataset_id)
        if dataset is None:
            raise DatasetNotFoundError(f"Dataset {dataset_id} não encontrado")
        df = self.reader.read_csv(dataset.stored_path)
        payload = self.service.run_isolation_forest(df, columns, contamination)
        result = AnalysisResult(id=str(uuid4()), dataset_id=dataset_id, analysis_type="isolation_forest", payload=payload)
        return self.results.save(result)
