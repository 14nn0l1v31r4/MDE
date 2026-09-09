from datetime import datetime, timezone
import pytest

from app.domain.entities.user import User
from app.domain.entities.dataset import Dataset
from app.domain.entities.analysis_result import AnalysisResult
from app.domain.exceptions.domain_exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserInactiveError,
    UnauthorizedAccessError,
    DatasetAccessForbiddenError,
)


def test_create_user_entity_defaults():
    user = User(
        id="user-123",
        email="analyst@test.com",
        hashed_password="hashed_pw_secret",
        full_name="Analista Teste",
    )
    assert user.id == "user-123"
    assert user.email == "analyst@test.com"
    assert user.hashed_password == "hashed_pw_secret"
    assert user.full_name == "Analista Teste"
    assert user.role == "analyst"
    assert user.is_active is True
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)


def test_dataset_entity_has_user_id():
    dataset = Dataset(
        id="ds-1",
        user_id="user-123",
        filename="turma.csv",
        stored_path="/storage/uploads/user-123/turma.csv",
        rows=100,
        columns=["nota", "presenca"],
    )
    assert dataset.user_id == "user-123"


def test_analysis_result_entity_has_user_id():
    result = AnalysisResult(
        id="res-1",
        dataset_id="ds-1",
        user_id="user-123",
        analysis_type="kmeans",
        payload={"clusters": 3},
    )
    assert result.user_id == "user-123"


def test_security_domain_exceptions():
    err1 = UserAlreadyExistsError("Email já cadastrado")
    assert "Email já cadastrado" in str(err1)

    err2 = InvalidCredentialsError("Credenciais inválidas")
    assert "Credenciais inválidas" in str(err2)

    err3 = UserInactiveError("Usuário inativo")
    assert "Usuário inativo" in str(err3)

    err4 = UnauthorizedAccessError("Acesso não autorizado")
    assert "Acesso não autorizado" in str(err4)

    err5 = DatasetAccessForbiddenError("Acesso negado ao dataset")
    assert "Acesso negado ao dataset" in str(err5)

