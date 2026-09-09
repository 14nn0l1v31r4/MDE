from datetime import timedelta
import pytest
import time

from app.domain.exceptions.domain_exceptions import UnauthorizedAccessError
from app.application.ports.security import PasswordHasher, TokenService
from app.infrastructure.security.bcrypt_hasher import BcryptPasswordHasher
from app.infrastructure.security.jwt_token_service import PyJWTSecurityTokenService


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

