from uuid import uuid4

from app.application.ports.analysis_services import AssociationRulesService, DatasetReader
from app.application.ports.repositories import AnalysisResultRepository, DatasetRepository
from app.domain.entities.analysis_result import AnalysisResult
from app.domain.exceptions.domain_exceptions import (
    DatasetNotFoundError,
    InvalidAnalysisInputError,
)


class MineAssociationRulesUseCase:
    def __init__(
        self,
        datasets: DatasetRepository,
        results: AnalysisResultRepository,
        reader: DatasetReader,
        service: AssociationRulesService,
    ):
        self.datasets = datasets
        self.results = results
        self.reader = reader
        self.service = service

    def execute(
        self,
        dataset_id: str,
        columns: list[str],
        min_support: float,
        min_confidence: float,
        user_id: str = "",
        is_admin: bool = False,
    ) -> AnalysisResult:
        if not columns:
            raise InvalidAnalysisInputError(
                "Informe ao menos uma coluna categórica para regras de associação"
            )
        dataset = self.datasets.get_by_id(dataset_id)
        if (
            dataset is None
            or not dataset.user_id
            or (user_id and not is_admin and dataset.user_id != user_id)
        ):
            raise DatasetNotFoundError(f"Dataset {dataset_id} não encontrado")
        df = self.reader.read_csv(dataset.stored_path)
        payload = self.service.mine_rules(df, columns, min_support, min_confidence)
        result = AnalysisResult(
            id=str(uuid4()),
            dataset_id=dataset_id,
            analysis_type="association_rules",
            payload=payload,
            user_id=user_id,
        )
        return self.results.save(result)
