from app.domain.entities.dataset import Dataset
from app.domain.entities.analysis_result import AnalysisResult


class InMemoryDatasetRepository:
    def __init__(self):
        self._items: dict[str, Dataset] = {}

    def save(self, dataset: Dataset) -> Dataset:
        self._items[dataset.id] = dataset
        return dataset

    def get_by_id(self, dataset_id: str) -> Dataset | None:
        return self._items.get(dataset_id)

    def list_all(self) -> list[Dataset]:
        return list(self._items.values())


class InMemoryAnalysisResultRepository:
    def __init__(self):
        self._items: dict[str, AnalysisResult] = {}

    def save(self, result: AnalysisResult) -> AnalysisResult:
        self._items[result.id] = result
        return result

    def get_by_id(self, result_id: str) -> AnalysisResult | None:
        return self._items.get(result_id)

    def list_by_dataset(self, dataset_id: str) -> list[AnalysisResult]:
        return [result for result in self._items.values() if result.dataset_id == dataset_id]
