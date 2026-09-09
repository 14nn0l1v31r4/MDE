from app.application.ports.repositories import DatasetRepository
from app.domain.entities.dataset import Dataset


class ListDatasetsUseCase:
    def __init__(self, repository: DatasetRepository):
        self.repository = repository

    def execute(self) -> list[Dataset]:
        return self.repository.list_all()
    def execute(self, user_id: str = "", is_admin: bool = False) -> list[Dataset]:
        if is_admin or not user_id:
            return self.repository.list_all()
        return self.repository.list_by_user(user_id)
