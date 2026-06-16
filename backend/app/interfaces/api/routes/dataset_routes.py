from fastapi import APIRouter, UploadFile, File, HTTPException
from app.application.use_cases.upload_dataset import UploadDatasetUseCase
from app.application.use_cases.list_datasets import ListDatasetsUseCase
from app.application.use_cases.preview_dataset import PreviewDatasetUseCase
from app.domain.exceptions.domain_exceptions import DatasetNotFoundError
from app.interfaces.api.dependencies import dataset_repository, file_storage, dataset_reader
from app.interfaces.api.schemas.dataset_schemas import DatasetResponse, DatasetPreviewResponse


router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Envie um arquivo CSV")
    content = await file.read()
    use_case = UploadDatasetUseCase(dataset_repository, file_storage, dataset_reader)
    try:
        return use_case.execute(file.filename, content)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=list[DatasetResponse])
def list_datasets():
    return ListDatasetsUseCase(dataset_repository).execute()


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def preview_dataset(dataset_id: str, limit: int = 10):
    use_case = PreviewDatasetUseCase(dataset_repository, dataset_reader)
    try:
        return use_case.execute(dataset_id, limit)
    except DatasetNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
