from datetime import timedelta
import io
import json
import logging

import pytest

from app.domain.exceptions.domain_exceptions import UnauthorizedAccessError
from app.application.ports.security import PasswordHasher, TokenService
from app.infrastructure.security.audit_logger import audit_event
from app.infrastructure.security.bcrypt_hasher import BcryptPasswordHasher
from app.infrastructure.security.jwt_token_service import PyJWTSecurityTokenService
from app.infrastructure.storage.local_file_storage import LocalFileStorage


def test_password_hasher_hash_and_verify():
    hasher: PasswordHasher = BcryptPasswordHasher()
    plain = "SuperSecret123!"
    hashed = hasher.hash(plain)

    assert hashed != plain
    assert hasher.verify(plain, hashed) is True
    assert hasher.verify("WrongSecret", hashed) is False


def test_jwt_token_service_create_and_decode():
    token_service: TokenService = PyJWTSecurityTokenService(
        secret_key="test_secret_key_at_least_32_characters_long",
        algorithm="HS256",
        expire_minutes=15,
    )
    payload_data = {"sub": "user-uuid-1", "role": "analyst"}
    token = token_service.create_access_token(payload_data)

    assert isinstance(token, str)
    assert len(token) > 20

    decoded = token_service.decode_token(token)
    assert decoded["sub"] == "user-uuid-1"
    assert decoded["role"] == "analyst"
    assert "exp" in decoded


def test_jwt_token_service_expired_token():
    token_service = PyJWTSecurityTokenService(
        secret_key="test_secret_key_at_least_32_characters_long",
        algorithm="HS256",
        expire_minutes=1,
    )
    # Token expired 1 second ago
    token = token_service.create_access_token({"sub": "user-expired"}, expires_delta=timedelta(seconds=-1))

    with pytest.raises(UnauthorizedAccessError, match="Token expirado"):
        token_service.decode_token(token)


def test_jwt_token_service_invalid_token():
    token_service = PyJWTSecurityTokenService(
        secret_key="test_secret_key_at_least_32_characters_long",
        algorithm="HS256",
    )
    with pytest.raises(UnauthorizedAccessError, match="Token inválido"):
        token_service.decode_token("invalid.jwt.token.string")


def test_audit_event_contains_context_without_sensitive_values(caplog):
    caplog.set_level(logging.INFO, logger="mde.audit")

    audit_event(
        "auth.login",
        actor_user_id="user-1",
        resource_id=None,
        outcome="success",
        correlation_id="corr-1",
        ip_address="127.0.0.1",
    )

    payload = json.loads(caplog.records[-1].message)
    assert payload == {
        "actor_user_id": "user-1",
        "correlation_id": "corr-1",
        "event": "auth.login",
        "ip_address": "127.0.0.1",
        "outcome": "success",
        "resource_id": None,
    }
    assert "password" not in payload
    assert "token" not in payload


def test_local_storage_streams_with_size_limit_and_validates_paths(tmp_path):
    storage = LocalFileStorage(str(tmp_path), max_size_bytes=8)

    stored_path = storage.save_stream(
        "grades.csv",
        io.BytesIO(b"a,b\n1,2\n"),
        user_id="user-1",
    )

    with open(stored_path, "rb") as stored_file:
        assert stored_file.read() == b"a,b\n1,2\n"
    assert storage.get_path(stored_path) == stored_path

    with pytest.raises(ValueError, match="Caminho"):
        storage.get_path(str(tmp_path.parent / "outside.csv"))


def test_local_storage_rejects_oversized_stream_without_partial_file(tmp_path):
    storage = LocalFileStorage(str(tmp_path), max_size_bytes=4)

    with pytest.raises(ValueError, match="tamanho máximo"):
        storage.save_stream("grades.csv", io.BytesIO(b"12345"), user_id="user-1")

    assert not list(tmp_path.rglob("*.part"))
    assert not list(tmp_path.rglob("*.csv"))
