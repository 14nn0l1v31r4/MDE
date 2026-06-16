from app.application.ports.repositories import DatasetRepository
from app.domain.entities.dataset import Dataset


class ListDatasetsUseCase:
    def __init__(self, repository: DatasetRepository):
        self.repository = repository

    def execute(self) -> list[Dataset]:
        return self.repository.list_all()
