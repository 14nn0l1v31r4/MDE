from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.analysis_result import AnalysisResult
from app.domain.entities.dataset import Dataset
from app.infrastructure.database.models import AnalysisResultModel, DatasetModel


class PostgresDatasetRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def save(self, dataset: Dataset) -> Dataset:
        with self.session_factory() as session:
            model = DatasetModel(
                id=dataset.id,
                filename=dataset.filename,
                stored_path=dataset.stored_path,
                rows=dataset.rows,
                columns=dataset.columns,
                created_at=dataset.created_at,
            )

            model = session.merge(model)
            session.commit()
            session.refresh(model)

            return self._to_entity(model)

    def get_by_id(self, dataset_id: str) -> Dataset | None:
        with self.session_factory() as session:
            model = session.get(DatasetModel, dataset_id)
            return self._to_entity(model) if model else None

    def list_all(self) -> list[Dataset]:
        with self.session_factory() as session:
            statement = select(DatasetModel).order_by(DatasetModel.created_at.desc())
            return [self._to_entity(model) for model in session.scalars(statement).all()]

    @staticmethod
    def _to_entity(model: DatasetModel) -> Dataset:
        return Dataset(
            id=model.id,
            filename=model.filename,
            stored_path=model.stored_path,
            rows=model.rows,
            columns=list(model.columns),
            created_at=model.created_at,
        )


class PostgresAnalysisResultRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def save(self, result: AnalysisResult) -> AnalysisResult:
        with self.session_factory() as session:
            model = AnalysisResultModel(
                id=result.id,
                dataset_id=result.dataset_id,
                analysis_type=result.analysis_type,
                payload=result.payload,
                created_at=result.created_at,
            )

            model = session.merge(model)
            session.commit()
            session.refresh(model)

            return self._to_entity(model)

    def get_by_id(self, result_id: str) -> AnalysisResult | None:
        with self.session_factory() as session:
            model = session.get(AnalysisResultModel, result_id)
            return self._to_entity(model) if model else None

    def list_by_dataset(self, dataset_id: str) -> list[AnalysisResult]:
        with self.session_factory() as session:
            statement = (
                select(AnalysisResultModel)
                .where(AnalysisResultModel.dataset_id == dataset_id)
                .order_by(AnalysisResultModel.created_at.desc())
            )
            return [self._to_entity(model) for model in session.scalars(statement).all()]

    @staticmethod
    def _to_entity(model: AnalysisResultModel) -> AnalysisResult:
        return AnalysisResult(
            id=model.id,
            dataset_id=model.dataset_id,
            analysis_type=model.analysis_type,
            payload=dict(model.payload),
            created_at=model.created_at,
        )