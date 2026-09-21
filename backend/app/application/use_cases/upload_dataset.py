from typing import BinaryIO
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

    def execute(self, filename: str, content: bytes, user_id: str = "") -> Dataset:
        stored_path = self.storage.save(filename, content, user_id=user_id)
        return self._persist_dataset(filename, stored_path, user_id)

    def execute_stream(self, filename: str, stream: BinaryIO, user_id: str = "") -> Dataset:
        stored_path = self.storage.save_stream(filename, stream, user_id=user_id)
        return self._persist_dataset(filename, stored_path, user_id)

    def _persist_dataset(self, filename: str, stored_path: str, user_id: str) -> Dataset:
        df = self.reader.read_csv(stored_path)
        dataset = Dataset(
            id=str(uuid4()),
            filename=filename,
            stored_path=stored_path,
            rows=int(df.shape[0]),
            columns=[str(column) for column in df.columns],
            user_id=user_id,
        )
        return self.repository.save(dataset)
