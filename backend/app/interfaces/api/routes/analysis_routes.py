from fastapi import APIRouter, HTTPException
from app.application.use_cases.run_statistics import RunStatisticsUseCase
from app.application.use_cases.run_kmeans import RunKMeansUseCase
from app.application.use_cases.run_dbscan import RunDBSCANUseCase
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.use_cases.detect_anomalies import DetectAnomaliesUseCase
from app.application.use_cases.mine_association_rules import MineAssociationRulesUseCase
from app.domain.exceptions.domain_exceptions import DatasetNotFoundError, InvalidAnalysisInputError
from app.application.use_cases.run_dbscan import RunDBSCANUseCase
from app.application.use_cases.run_kmeans import RunKMeansUseCase
from app.application.use_cases.run_statistics import RunStatisticsUseCase
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import (
    DatasetNotFoundError,
    InvalidAnalysisInputError,
)
from app.interfaces.api.dependencies import (
    dataset_repository,
    analysis_result_repository,
    anomaly_detection_service,
    association_rules_service,
    clustering_service,
    dataset_reader,
    dataset_repository,
    get_current_active_user,
    statistics_service,
    clustering_service,
    anomaly_detection_service,
    association_rules_service,
)
from app.interfaces.api.schemas.analysis_schemas import (
    AnalysisResultResponse,
    AssociationRulesRequest,
    DatasetAnalysisRequest,
    KMeansRequest,
    DBSCANRequest,
    IsolationForestRequest,
    AssociationRulesRequest,
    AnalysisResultResponse,
    KMeansRequest,
)


router = APIRouter(prefix="/analysis", tags=["Analysis"])


def _handle_errors(error: Exception):
    if isinstance(error, DatasetNotFoundError):
        raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    if isinstance(error, InvalidAnalysisInputError):
        raise HTTPException(status_code=400, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.post("/statistics", response_model=AnalysisResultResponse)
def run_statistics(request: DatasetAnalysisRequest):
def run_statistics(
    request: DatasetAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
):
    try:
        use_case = RunStatisticsUseCase(dataset_repository, analysis_result_repository, dataset_reader, statistics_service)
        return use_case.execute(request.dataset_id)
        is_admin = current_user.role == "admin"
        use_case = RunStatisticsUseCase(
            dataset_repository,
            analysis_result_repository,
            dataset_reader,
            statistics_service,
        )
        return use_case.execute(
            dataset_id=request.dataset_id,
            user_id=current_user.id,
            is_admin=is_admin,
        )
    except Exception as error:
        _handle_errors(error)


@router.post("/clustering/kmeans", response_model=AnalysisResultResponse)
def run_kmeans(request: KMeansRequest):
def run_kmeans(
    request: KMeansRequest,
    current_user: User = Depends(get_current_active_user),
):
    try:
        use_case = RunKMeansUseCase(dataset_repository, analysis_result_repository, dataset_reader, clustering_service)
        return use_case.execute(request.dataset_id, request.columns, request.n_clusters)
        is_admin = current_user.role == "admin"
        use_case = RunKMeansUseCase(
            dataset_repository,
            analysis_result_repository,
            dataset_reader,
            clustering_service,
        )
        return use_case.execute(
            dataset_id=request.dataset_id,
            columns=request.columns,
            n_clusters=request.n_clusters,
            user_id=current_user.id,
            is_admin=is_admin,
        )
    except Exception as error:
        _handle_errors(error)


@router.post("/clustering/dbscan", response_model=AnalysisResultResponse)
def run_dbscan(request: DBSCANRequest):
def run_dbscan(
    request: DBSCANRequest,
    current_user: User = Depends(get_current_active_user),
):
    try:
        use_case = RunDBSCANUseCase(dataset_repository, analysis_result_repository, dataset_reader, clustering_service)
        return use_case.execute(request.dataset_id, request.columns, request.eps, request.min_samples)
        is_admin = current_user.role == "admin"
        use_case = RunDBSCANUseCase(
            dataset_repository,
            analysis_result_repository,
            dataset_reader,
            clustering_service,
        )
        return use_case.execute(
            dataset_id=request.dataset_id,
            columns=request.columns,
            eps=request.eps,
            min_samples=request.min_samples,
            user_id=current_user.id,
            is_admin=is_admin,
        )
    except Exception as error:
        _handle_errors(error)


@router.post("/anomalies/isolation-forest", response_model=AnalysisResultResponse)
def run_isolation_forest(request: IsolationForestRequest):
def run_isolation_forest(
    request: IsolationForestRequest,
    current_user: User = Depends(get_current_active_user),
):
    try:
        use_case = DetectAnomaliesUseCase(dataset_repository, analysis_result_repository, dataset_reader, anomaly_detection_service)
        return use_case.execute(request.dataset_id, request.columns, request.contamination)
        is_admin = current_user.role == "admin"
        use_case = DetectAnomaliesUseCase(
            dataset_repository,
            analysis_result_repository,
            dataset_reader,
            anomaly_detection_service,
        )
        return use_case.execute(
            dataset_id=request.dataset_id,
            columns=request.columns,
            contamination=request.contamination,
            user_id=current_user.id,
            is_admin=is_admin,
        )
    except Exception as error:
        _handle_errors(error)


@router.post("/association-rules", response_model=AnalysisResultResponse)
def mine_association_rules(request: AssociationRulesRequest):
def mine_association_rules(
    request: AssociationRulesRequest,
    current_user: User = Depends(get_current_active_user),
):
    try:
        use_case = MineAssociationRulesUseCase(dataset_repository, analysis_result_repository, dataset_reader, association_rules_service)
        return use_case.execute(request.dataset_id, request.columns, request.min_support, request.min_confidence)
        is_admin = current_user.role == "admin"
        use_case = MineAssociationRulesUseCase(
            dataset_repository,
            analysis_result_repository,
            dataset_reader,
            association_rules_service,
        )
        return use_case.execute(
            dataset_id=request.dataset_id,
            columns=request.columns,
            min_support=request.min_support,
            min_confidence=request.min_confidence,
            user_id=current_user.id,
            is_admin=is_admin,
        )
    except Exception as error:
        _handle_errors(error)
