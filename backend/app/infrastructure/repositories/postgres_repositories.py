from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.analysis_result import AnalysisResult
from app.domain.entities.dataset import Dataset
from app.infrastructure.database.models import AnalysisResultModel, DatasetModel
from app.domain.entities.user import User
from app.infrastructure.database.models import (
    AnalysisResultModel,
    DatasetModel,
    UserModel,
)


class PostgresUserRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def save(self, user: User) -> User:
        with self.session_factory() as session:
            model = UserModel(
                id=user.id,
                email=user.email,
                hashed_password=user.hashed_password,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            model = session.merge(model)
            session.commit()
            session.refresh(model)
            return self._to_entity(model)

    def get_by_id(self, user_id: str) -> User | None:
        with self.session_factory() as session:
            model = session.get(UserModel, user_id)
            return self._to_entity(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        with self.session_factory() as session:
            statement = select(UserModel).where(UserModel.email == email.strip().lower())
            model = session.scalar(statement)
            return self._to_entity(model) if model else None

    def list_all(self) -> list[User]:
        with self.session_factory() as session:
            statement = select(UserModel).order_by(UserModel.created_at.desc())
            return [self._to_entity(model) for model in session.scalars(statement).all()]

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            role=model.role,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class PostgresDatasetRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def save(self, dataset: Dataset) -> Dataset:
        with self.session_factory() as session:
            model = DatasetModel(
                id=dataset.id,
                user_id=dataset.user_id if dataset.user_id else None,
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

    def list_by_user(self, user_id: str) -> list[Dataset]:
        with self.session_factory() as session:
            statement = (
                select(DatasetModel)
                .where(DatasetModel.user_id == user_id)
                .order_by(DatasetModel.created_at.desc())
            )
            return [self._to_entity(model) for model in session.scalars(statement).all()]

    @staticmethod
    def _to_entity(model: DatasetModel) -> Dataset:
        return Dataset(
            id=model.id,
            filename=model.filename,
            stored_path=model.stored_path,
            rows=model.rows,
            columns=list(model.columns),
            user_id=model.user_id or "",
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
                user_id=result.user_id if result.user_id else None,
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

    def list_by_user(self, user_id: str) -> list[AnalysisResult]:
        with self.session_factory() as session:
            statement = (
                select(AnalysisResultModel)
                .where(AnalysisResultModel.user_id == user_id)
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
            user_id=model.user_id or "",
            created_at=model.created_at,
        )