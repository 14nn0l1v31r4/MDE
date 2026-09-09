from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from app.application.use_cases.list_datasets import ListDatasetsUseCase
from app.application.use_cases.preview_dataset import PreviewDatasetUseCase
from app.application.use_cases.upload_dataset import UploadDatasetUseCase
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import DatasetNotFoundError
from app.infrastructure.security.audit_logger import audit_request_event
from app.interfaces.api import dependencies as deps
from app.interfaces.api.dependencies import get_current_active_user
from app.interfaces.api.schemas.dataset_schemas import DatasetPreviewResponse, DatasetResponse


router = APIRouter(prefix="/datasets", tags=["Datasets"])
ALLOWED_CSV_CONTENT_TYPES = {"text/csv", "text/plain", "application/csv"}


def _validate_upload(file: UploadFile) -> None:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo inválido. Apenas arquivos no formato CSV são permitidos.",
        )
    if file.content_type not in ALLOWED_CSV_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Tipo de conteúdo inválido. Envie um CSV.",
        )


@router.post("/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
):
    try:
        _validate_upload(file)
        await file.seek(0)
        dataset = UploadDatasetUseCase(
            deps.dataset_repository,
            deps.file_storage,
            deps.dataset_reader,
        ).execute_stream(
            file.filename,
            file.file,
            user_id=current_user.id,
        )
        audit_request_event(
            request,
            "dataset.upload",
            actor_user_id=current_user.id,
            resource_id=dataset.id,
            outcome="success",
        )
        return dataset
    except HTTPException:
        audit_request_event(
            request,
            "dataset.upload",
            actor_user_id=current_user.id,
            outcome="rejected",
        )
        raise
    except ValueError as error:
        audit_request_event(
            request,
            "dataset.upload",
            actor_user_id=current_user.id,
            outcome="rejected",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo CSV inválido ou excede o limite permitido.",
        ) from error


@router.get("", response_model=list[DatasetResponse])
def list_datasets(
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    is_admin = current_user.role == "admin"
    datasets = ListDatasetsUseCase(deps.dataset_repository).execute(
        user_id=current_user.id,
        is_admin=is_admin,
    )
    audit_request_event(
        request,
        "dataset.list",
        actor_user_id=current_user.id,
        outcome="success",
    )
    return datasets


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def preview_dataset(
    request: Request,
    dataset_id: str,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
):
    is_admin = current_user.role == "admin"
    use_case = PreviewDatasetUseCase(deps.dataset_repository, deps.dataset_reader)
    try:
        result = use_case.execute(
            dataset_id=dataset_id,
            limit=limit,
            user_id=current_user.id,
            is_admin=is_admin,
        )
        audit_request_event(
            request,
            "dataset.preview",
            actor_user_id=current_user.id,
            resource_id=dataset_id,
            outcome="success",
        )
        return result
    except DatasetNotFoundError as error:
        audit_request_event(
            request,
            "dataset.preview",
            actor_user_id=current_user.id,
            resource_id=dataset_id,
            outcome="denied",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset não encontrado",
        ) from error
