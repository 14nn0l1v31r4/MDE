from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.application.use_cases.detect_anomalies import DetectAnomaliesUseCase
from app.application.use_cases.mine_association_rules import MineAssociationRulesUseCase
from app.application.use_cases.run_dbscan import RunDBSCANUseCase
from app.application.use_cases.run_kmeans import RunKMeansUseCase
from app.application.use_cases.run_statistics import RunStatisticsUseCase
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import DatasetNotFoundError, InvalidAnalysisInputError
from app.infrastructure.security.audit_logger import audit_request_event
from app.interfaces.api import dependencies as deps
from app.interfaces.api.dependencies import get_current_active_user
from app.interfaces.api.schemas.analysis_schemas import (
    AnalysisResultResponse,
    AssociationRulesRequest,
    DBSCANRequest,
    DatasetAnalysisRequest,
    IsolationForestRequest,
    KMeansRequest,
)


router = APIRouter(prefix="/analysis", tags=["Analysis"])


def _raise_analysis_error(
    request: Request,
    current_user: User,
    dataset_id: str,
    error: Exception,
) -> None:
    if isinstance(error, DatasetNotFoundError):
        audit_request_event(
            request,
            "analysis.run",
            actor_user_id=current_user.id,
            resource_id=dataset_id,
            outcome="denied",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset não encontrado",
        ) from error
    if isinstance(error, InvalidAnalysisInputError):
        audit_request_event(
            request,
            "analysis.run",
            actor_user_id=current_user.id,
            resource_id=dataset_id,
            outcome="rejected",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    raise error


def _run_analysis(
    request: Request,
    current_user: User,
    dataset_id: str,
    execute: Callable[[], Any],
):
    try:
        result = execute()
    except (DatasetNotFoundError, InvalidAnalysisInputError) as error:
        _raise_analysis_error(request, current_user, dataset_id, error)
    audit_request_event(
        request,
        "analysis.run",
        actor_user_id=current_user.id,
        resource_id=dataset_id,
        outcome="success",
    )
    return result


@router.post("/statistics", response_model=AnalysisResultResponse)
def run_statistics(
    request: Request,
    body: DatasetAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
):
    is_admin = current_user.role == "admin"
    use_case = RunStatisticsUseCase(
        deps.dataset_repository,
        deps.analysis_result_repository,
        deps.dataset_reader,
        deps.statistics_service,
    )
    return _run_analysis(
        request,
        current_user,
        body.dataset_id,
        lambda: use_case.execute(body.dataset_id, user_id=current_user.id, is_admin=is_admin),
    )


@router.post("/clustering/kmeans", response_model=AnalysisResultResponse)
def run_kmeans(
    request: Request,
    body: KMeansRequest,
    current_user: User = Depends(get_current_active_user),
):
    is_admin = current_user.role == "admin"
    use_case = RunKMeansUseCase(
        deps.dataset_repository,
        deps.analysis_result_repository,
        deps.dataset_reader,
        deps.clustering_service,
    )
    return _run_analysis(
        request,
        current_user,
        body.dataset_id,
        lambda: use_case.execute(
            body.dataset_id,
            body.columns,
            body.n_clusters,
            user_id=current_user.id,
            is_admin=is_admin,
        ),
    )


@router.post("/clustering/dbscan", response_model=AnalysisResultResponse)
def run_dbscan(
    request: Request,
    body: DBSCANRequest,
    current_user: User = Depends(get_current_active_user),
):
    is_admin = current_user.role == "admin"
    use_case = RunDBSCANUseCase(
        deps.dataset_repository,
        deps.analysis_result_repository,
        deps.dataset_reader,
        deps.clustering_service,
    )
    return _run_analysis(
        request,
        current_user,
        body.dataset_id,
        lambda: use_case.execute(
            body.dataset_id,
            body.columns,
            body.eps,
            body.min_samples,
            user_id=current_user.id,
            is_admin=is_admin,
        ),
    )


@router.post("/anomalies/isolation-forest", response_model=AnalysisResultResponse)
def run_isolation_forest(
    request: Request,
    body: IsolationForestRequest,
    current_user: User = Depends(get_current_active_user),
):
    is_admin = current_user.role == "admin"
    use_case = DetectAnomaliesUseCase(
        deps.dataset_repository,
        deps.analysis_result_repository,
        deps.dataset_reader,
        deps.anomaly_detection_service,
    )
    return _run_analysis(
        request,
        current_user,
        body.dataset_id,
        lambda: use_case.execute(
            body.dataset_id,
            body.columns,
            body.contamination,
            user_id=current_user.id,
            is_admin=is_admin,
        ),
    )


@router.post("/association-rules", response_model=AnalysisResultResponse)
def mine_association_rules(
    request: Request,
    body: AssociationRulesRequest,
    current_user: User = Depends(get_current_active_user),
):
    is_admin = current_user.role == "admin"
    use_case = MineAssociationRulesUseCase(
        deps.dataset_repository,
        deps.analysis_result_repository,
        deps.dataset_reader,
        deps.association_rules_service,
    )
    return _run_analysis(
        request,
        current_user,
        body.dataset_id,
        lambda: use_case.execute(
            body.dataset_id,
            body.columns,
            body.min_support,
            body.min_confidence,
            user_id=current_user.id,
            is_admin=is_admin,
        ),
    )
