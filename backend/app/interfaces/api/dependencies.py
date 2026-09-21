from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.application.use_cases.get_current_user import GetCurrentUserUseCase
from app.config.settings import settings
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import (
    UnauthorizedAccessError,
    UserInactiveError,
)
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.repositories.postgres_repositories import (
    PostgresAnalysisResultRepository,
    PostgresDatasetRepository,
    PostgresUserRepository,
)
from app.infrastructure.storage.local_file_storage import LocalFileStorage
from app.infrastructure.security.bcrypt_hasher import BcryptPasswordHasher
from app.infrastructure.security.jwt_token_service import PyJWTSecurityTokenService
from app.infrastructure.services.anomaly_detection_service import SklearnAnomalyDetectionService
from app.infrastructure.services.association_rules_service import MlxtendAssociationRulesService
from app.infrastructure.services.clustering_service import SklearnClusteringService
from app.infrastructure.services.pandas_dataset_reader import PandasDatasetReader
from app.infrastructure.services.statistics_service import PandasStatisticsService
from app.infrastructure.services.clustering_service import SklearnClusteringService
from app.infrastructure.services.anomaly_detection_service import SklearnAnomalyDetectionService
from app.infrastructure.services.association_rules_service import MlxtendAssociationRulesService
from app.infrastructure.storage.local_file_storage import LocalFileStorage


# Singletons / Services
user_repository = PostgresUserRepository(SessionLocal)
dataset_repository = PostgresDatasetRepository(SessionLocal)
analysis_result_repository = PostgresAnalysisResultRepository(SessionLocal)
file_storage = LocalFileStorage(settings.upload_dir)
password_hasher = BcryptPasswordHasher()
token_service = PyJWTSecurityTokenService(
    secret_key=settings.jwt_secret_key,
    algorithm=settings.jwt_algorithm,
    expire_minutes=settings.jwt_access_token_expire_minutes,
)
file_storage = LocalFileStorage(
    base_dir=settings.upload_dir,
    max_size_bytes=settings.max_upload_size_bytes,
)
dataset_reader = PandasDatasetReader()
statistics_service = PandasStatisticsService()
clustering_service = SklearnClusteringService()
anomaly_detection_service = SklearnAnomalyDetectionService()
association_rules_service = MlxtendAssociationRulesService()

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    use_case = GetCurrentUserUseCase(user_repository, token_service)
    try:
        return use_case.execute(token)
    except UnauthorizedAccessError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except UserInactiveError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Contate o suporte.",
        )
    return current_user


def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão insuficiente. Requer papel: {required_role}",
            )
        return current_user

    return role_checker
