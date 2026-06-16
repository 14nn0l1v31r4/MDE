from uuid import uuid4
from app.application.ports.repositories import DatasetRepository, AnalysisResultRepository
from app.application.ports.analysis_services import DatasetReader, ClusteringService
from app.domain.entities.analysis_result import AnalysisResult
from app.domain.exceptions.domain_exceptions import DatasetNotFoundError


class RunKMeansUseCase:
    def __init__(self, datasets: DatasetRepository, results: AnalysisResultRepository, reader: DatasetReader, service: ClusteringService):
        self.datasets = datasets
        self.results = results
        self.reader = reader
        self.service = service

    def execute(self, dataset_id: str, columns: list[str] | None, n_clusters: int) -> AnalysisResult:
        dataset = self.datasets.get_by_id(dataset_id)
        if dataset is None:
            raise DatasetNotFoundError(f"Dataset {dataset_id} não encontrado")
        df = self.reader.read_csv(dataset.stored_path)
        payload = self.service.run_kmeans(df, columns, n_clusters)
        result = AnalysisResult(id=str(uuid4()), dataset_id=dataset_id, analysis_type="kmeans", payload=payload)
        return self.results.save(result)
