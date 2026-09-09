import pytest
from app.domain.entities.dataset import Dataset
from app.domain.exceptions.domain_exceptions import DatasetNotFoundError
from app.application.use_cases.upload_dataset import UploadDatasetUseCase
from app.application.use_cases.list_datasets import ListDatasetsUseCase
from app.application.use_cases.preview_dataset import PreviewDatasetUseCase
from app.application.use_cases.run_statistics import RunStatisticsUseCase


class InMemoryDatasetRepository:
    def __init__(self):
        self.datasets: dict[str, Dataset] = {}

    def save(self, dataset: Dataset) -> Dataset:
        self.datasets[dataset.id] = dataset
        return dataset

    def get_by_id(self, dataset_id: str) -> Dataset | None:
        return self.datasets.get(dataset_id)

    def list_all(self) -> list[Dataset]:
        return list(self.datasets.values())

    def list_by_user(self, user_id: str) -> list[Dataset]:
        return [ds for ds in self.datasets.values() if ds.user_id == user_id]


class FakeStorage:
    def save(self, filename: str, content: bytes, user_id: str = "") -> str:
        return f"/storage/uploads/{user_id}/{filename}"


class FakeReader:
    def read_csv(self, path: str):
        import pandas as pd
        return pd.DataFrame({"col1": [1, 2, 3], "col2": [10, 20, 30]})


class FakeAnalysisRepository:
    def __init__(self):
        self.results = []

    def save(self, result):
        self.results.append(result)
        return result


class FakeStatisticsService:
    def summarize(self, df):
        return {"summary": "ok"}


def test_upload_and_list_datasets_isolated_by_user():
    repo = InMemoryDatasetRepository()
    storage = FakeStorage()
    reader = FakeReader()

    upload_case = UploadDatasetUseCase(repo, storage, reader)
    ds_user1 = upload_case.execute("user1_grades.csv", b"dummy_content", user_id="user-1")
    ds_user2 = upload_case.execute("user2_grades.csv", b"dummy_content", user_id="user-2")

    assert ds_user1.user_id == "user-1"
    assert ds_user2.user_id == "user-2"

    list_case = ListDatasetsUseCase(repo)
    user1_datasets = list_case.execute(user_id="user-1")
    user2_datasets = list_case.execute(user_id="user-2")

    assert len(user1_datasets) == 1
    assert user1_datasets[0].id == ds_user1.id
    assert len(user2_datasets) == 1
    assert user2_datasets[0].id == ds_user2.id


def test_preview_dataset_anti_idor_protection():
    repo = InMemoryDatasetRepository()
    storage = FakeStorage()
    reader = FakeReader()

    upload_case = UploadDatasetUseCase(repo, storage, reader)
    ds_user1 = upload_case.execute("secret.csv", b"data", user_id="user-1")

    preview_case = PreviewDatasetUseCase(repo, reader)

    # User 1 can preview own dataset
    result = preview_case.execute(ds_user1.id, user_id="user-1")
    assert result["dataset_id"] == ds_user1.id

    # User 2 receives 404 (anti-IDOR: does not reveal dataset existence)
    with pytest.raises(DatasetNotFoundError):
        preview_case.execute(ds_user1.id, user_id="user-2")


def test_run_statistics_anti_idor_protection():
    repo = InMemoryDatasetRepository()
    results_repo = FakeAnalysisRepository()
    reader = FakeReader()
    service = FakeStatisticsService()

    upload_case = UploadDatasetUseCase(repo, FakeStorage(), reader)
    ds_user1 = upload_case.execute("secret.csv", b"data", user_id="user-1")

    stat_case = RunStatisticsUseCase(repo, results_repo, reader, service)

    # User 1 can run
    analysis = stat_case.execute(ds_user1.id, user_id="user-1")
    assert analysis.user_id == "user-1"

    # User 2 receives DatasetNotFoundError
    with pytest.raises(DatasetNotFoundError):
        stat_case.execute(ds_user1.id, user_id="user-2")

