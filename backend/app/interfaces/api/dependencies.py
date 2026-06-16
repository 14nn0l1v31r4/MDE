from app.config.settings import settings
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.repositories.postgres_repositories import (
    PostgresAnalysisResultRepository,
    PostgresDatasetRepository,
)
from app.infrastructure.storage.local_file_storage import LocalFileStorage
from app.infrastructure.services.pandas_dataset_reader import PandasDatasetReader
from app.infrastructure.services.statistics_service import PandasStatisticsService
from app.infrastructure.services.clustering_service import SklearnClusteringService
from app.infrastructure.services.anomaly_detection_service import SklearnAnomalyDetectionService
from app.infrastructure.services.association_rules_service import MlxtendAssociationRulesService


dataset_repository = PostgresDatasetRepository(SessionLocal)
analysis_result_repository = PostgresAnalysisResultRepository(SessionLocal)
file_storage = LocalFileStorage(settings.upload_dir)
dataset_reader = PandasDatasetReader()
statistics_service = PandasStatisticsService()
clustering_service = SklearnClusteringService()
anomaly_detection_service = SklearnAnomalyDetectionService()
association_rules_service = MlxtendAssociationRulesService()
