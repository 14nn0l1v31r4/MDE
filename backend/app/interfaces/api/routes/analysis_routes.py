from fastapi import APIRouter, HTTPException
from app.application.use_cases.run_statistics import RunStatisticsUseCase
from app.application.use_cases.run_kmeans import RunKMeansUseCase
from app.application.use_cases.run_dbscan import RunDBSCANUseCase
from app.application.use_cases.detect_anomalies import DetectAnomaliesUseCase
from app.application.use_cases.mine_association_rules import MineAssociationRulesUseCase
from app.domain.exceptions.domain_exceptions import DatasetNotFoundError, InvalidAnalysisInputError
from app.interfaces.api.dependencies import (
    dataset_repository,
    analysis_result_repository,
    dataset_reader,
    statistics_service,
    clustering_service,
    anomaly_detection_service,
    association_rules_service,
)
from app.interfaces.api.schemas.analysis_schemas import (
    DatasetAnalysisRequest,
    KMeansRequest,
    DBSCANRequest,
    IsolationForestRequest,
    AssociationRulesRequest,
    AnalysisResultResponse,
)


router = APIRouter(prefix="/analysis", tags=["Analysis"])


def _handle_errors(error: Exception):
    if isinstance(error, DatasetNotFoundError):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, InvalidAnalysisInputError):
        raise HTTPException(status_code=400, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/statistics", response_model=AnalysisResultResponse)
def run_statistics(request: DatasetAnalysisRequest):
    try:
        use_case = RunStatisticsUseCase(dataset_repository, analysis_result_repository, dataset_reader, statistics_service)
        return use_case.execute(request.dataset_id)
    except Exception as error:
        _handle_errors(error)


@router.post("/clustering/kmeans", response_model=AnalysisResultResponse)
def run_kmeans(request: KMeansRequest):
    try:
        use_case = RunKMeansUseCase(dataset_repository, analysis_result_repository, dataset_reader, clustering_service)
        return use_case.execute(request.dataset_id, request.columns, request.n_clusters)
    except Exception as error:
        _handle_errors(error)


@router.post("/clustering/dbscan", response_model=AnalysisResultResponse)
def run_dbscan(request: DBSCANRequest):
    try:
        use_case = RunDBSCANUseCase(dataset_repository, analysis_result_repository, dataset_reader, clustering_service)
        return use_case.execute(request.dataset_id, request.columns, request.eps, request.min_samples)
    except Exception as error:
        _handle_errors(error)


@router.post("/anomalies/isolation-forest", response_model=AnalysisResultResponse)
def run_isolation_forest(request: IsolationForestRequest):
    try:
        use_case = DetectAnomaliesUseCase(dataset_repository, analysis_result_repository, dataset_reader, anomaly_detection_service)
        return use_case.execute(request.dataset_id, request.columns, request.contamination)
    except Exception as error:
        _handle_errors(error)


@router.post("/association-rules", response_model=AnalysisResultResponse)
def mine_association_rules(request: AssociationRulesRequest):
    try:
        use_case = MineAssociationRulesUseCase(dataset_repository, analysis_result_repository, dataset_reader, association_rules_service)
        return use_case.execute(request.dataset_id, request.columns, request.min_support, request.min_confidence)
    except Exception as error:
        _handle_errors(error)
