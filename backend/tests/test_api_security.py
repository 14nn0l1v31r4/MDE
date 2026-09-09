import io
import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

import app.interfaces.api.dependencies as deps
from app.infrastructure.repositories.in_memory_repositories import (
    InMemoryAnalysisResultRepository,
    InMemoryDatasetRepository,
    InMemoryUserRepository,
)
from app.infrastructure.storage.local_file_storage import LocalFileStorage
from app.interfaces.api.main import app


@pytest.fixture(autouse=True)
def setup_in_memory_backends(tmp_path):
    # Set fresh in-memory repos and temp storage for API tests
    deps.user_repository = InMemoryUserRepository()
    deps.dataset_repository = InMemoryDatasetRepository()
    deps.analysis_result_repository = InMemoryAnalysisResultRepository()
    deps.file_storage = LocalFileStorage(base_dir=str(tmp_path / "uploads"))


@pytest.fixture
def client():
    return TestClient(app)


def test_anonymous_access_is_denied(client):
    # 100% of business endpoints must reject anonymous calls with 401
    r_list = client.get("/api/datasets")
    assert r_list.status_code == 401
    assert "WWW-Authenticate" in r_list.headers

    r_preview = client.get("/api/datasets/random-id/preview")
    assert r_preview.status_code == 401

    r_stats = client.post("/api/analysis/statistics", json={"dataset_id": "random-id"})
    assert r_stats.status_code == 401

    r_kmeans = client.post(
        "/api/analysis/clustering/kmeans",
        json={"dataset_id": "random-id", "n_clusters": 3},
    )
    assert r_kmeans.status_code == 401

    r_me = client.get("/api/auth/me")
    assert r_me.status_code == 401


def test_public_routes(client):
    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json() == {"status": "ok"}


def test_security_headers_present(client):
    res = client.get("/health")
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert "Strict-Transport-Security" in res.headers


def test_full_authentication_and_data_isolation_flow(client):
    # 1. Register User 1
    r_reg1 = client.post(
        "/api/auth/register",
        json={
            "email": "user1@universidade.edu.br",
            "password": "StrongPassword123!",
            "full_name": "Primeiro Usuario",
            "role": "analyst",
        },
    )
    assert r_reg1.status_code == 201
    user1_id = r_reg1.json()["id"]

    # 2. Login User 1 (JSON)
    r_login1 = client.post(
        "/api/auth/login/json",
        json={
            "email": "user1@universidade.edu.br",
            "password": "StrongPassword123!",
        },
    )
    assert r_login1.status_code == 200
    token1 = r_login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # 3. Access /api/auth/me
    r_me1 = client.get("/api/auth/me", headers=headers1)
    assert r_me1.status_code == 200
    assert r_me1.json()["id"] == user1_id
    assert r_me1.json()["email"] == "user1@universidade.edu.br"

    # 4. Upload Dataset as User 1
    csv_content = b"nota_final,frequencia,horas_estudo\n8.5,90,12\n7.0,80,8\n9.2,95,15\n"
    files = {"file": ("turma_a.csv", io.BytesIO(csv_content), "text/csv")}
    r_upload1 = client.post("/api/datasets/upload", headers=headers1, files=files)
    assert r_upload1.status_code == 201
    ds1_id = r_upload1.json()["id"]
    assert r_upload1.json()["filename"] == "turma_a.csv"

    # 5. User 1 lists datasets -> sees 1 dataset
    r_list1 = client.get("/api/datasets", headers=headers1)
    assert r_list1.status_code == 200
    assert len(r_list1.json()) == 1
    assert r_list1.json()[0]["id"] == ds1_id

    # 6. User 1 previews own dataset
    r_prev1 = client.get(f"/api/datasets/{ds1_id}/preview", headers=headers1)
    assert r_prev1.status_code == 200
    assert len(r_prev1.json()["rows"]) == 3

    # 7. User 1 runs statistics
    r_stat1 = client.post(
        "/api/analysis/statistics",
        headers=headers1,
        json={"dataset_id": ds1_id},
    )
    assert r_stat1.status_code == 200
    assert r_stat1.json()["dataset_id"] == ds1_id

    # 8. Register and Login User 2
    client.post(
        "/api/auth/register",
        json={
            "email": "user2@universidade.edu.br",
            "password": "StrongPassword456!",
            "full_name": "Segundo Usuario",
            "role": "analyst",
        },
    )
    r_login2 = client.post(
        "/api/auth/login",
        data={
            "username": "user2@universidade.edu.br",
            "password": "StrongPassword456!",
        },
    )
    assert r_login2.status_code == 200
    token2 = r_login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 9. User 2 lists datasets -> sees EMPTY list (strict user data isolation!)
    r_list2 = client.get("/api/datasets", headers=headers2)
    assert r_list2.status_code == 200
    assert len(r_list2.json()) == 0

    # 10. User 2 attempts to preview User 1's dataset -> 404 Not Found (anti-IDOR!)
    r_prev2 = client.get(f"/api/datasets/{ds1_id}/preview", headers=headers2)
    assert r_prev2.status_code == 404

    # 11. User 2 attempts to run analysis on User 1's dataset -> 404 Not Found (anti-IDOR!)
    r_stat2 = client.post(
        "/api/analysis/statistics",
        headers=headers2,
        json={"dataset_id": ds1_id},
    )
    assert r_stat2.status_code == 404
