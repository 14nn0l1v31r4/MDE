from fastapi import APIRouter, UploadFile, File, HTTPException
from app.application.use_cases.upload_dataset import UploadDatasetUseCase
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.application.use_cases.list_datasets import ListDatasetsUseCase
from app.application.use_cases.preview_dataset import PreviewDatasetUseCase
from app.application.use_cases.upload_dataset import UploadDatasetUseCase
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import DatasetNotFoundError
from app.interfaces.api.dependencies import dataset_repository, file_storage, dataset_reader
from app.interfaces.api.schemas.dataset_schemas import DatasetResponse, DatasetPreviewResponse
from app.interfaces.api.dependencies import (
    dataset_reader,
    dataset_repository,
    file_storage,
    get_current_active_user,
)
from app.interfaces.api.schemas.dataset_schemas import (
    DatasetPreviewResponse,
    DatasetResponse,
)


router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Envie um arquivo CSV")
@router.post("/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo inválido. Apenas arquivos no formato CSV são permitidos.",
        )
    content = await file.read()
    use_case = UploadDatasetUseCase(dataset_repository, file_storage, dataset_reader)
    try:
        return use_case.execute(file.filename, content)
        return use_case.execute(file.filename, content, user_id=current_user.id)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        ) from val_err
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Falha ao processar upload: {error}",
        ) from error


@router.get("", response_model=list[DatasetResponse])
def list_datasets():
    return ListDatasetsUseCase(dataset_repository).execute()
def list_datasets(current_user: User = Depends(get_current_active_user)):
    is_admin = current_user.role == "admin"
    return ListDatasetsUseCase(dataset_repository).execute(
        user_id=current_user.id,
        is_admin=is_admin,
    )


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def preview_dataset(dataset_id: str, limit: int = 10):
def preview_dataset(
    dataset_id: str,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
):
    is_admin = current_user.role == "admin"
    use_case = PreviewDatasetUseCase(dataset_repository, dataset_reader)
    try:
        return use_case.execute(dataset_id, limit)
        return use_case.execute(
            dataset_id=dataset_id,
            limit=limit,
            user_id=current_user.id,
            is_admin=is_admin,
        )
    except DatasetNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
