from uuid import uuid4
from app.application.ports.repositories import DatasetRepository
from app.application.ports.storage import FileStorage
from app.application.ports.analysis_services import DatasetReader
from app.domain.entities.dataset import Dataset


class UploadDatasetUseCase:
    def __init__(self, repository: DatasetRepository, storage: FileStorage, reader: DatasetReader):
        self.repository = repository
        self.storage = storage
        self.reader = reader

    def execute(self, filename: str, content: bytes) -> Dataset:
        stored_path = self.storage.save(filename, content)
        df = self.reader.read_csv(stored_path)
        dataset = Dataset(
            id=str(uuid4()),
            filename=filename,
            stored_path=stored_path,
            rows=int(df.shape[0]),
            columns=[str(column) for column in df.columns],
        )
        return self.repository.save(dataset)
