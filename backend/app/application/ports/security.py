from datetime import timedelta
from typing import Any, Protocol


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str:
        ...

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        ...


class TokenService(Protocol):
    def create_access_token(
        self, data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> str:
        ...

    def decode_token(self, token: str) -> dict[str, Any]:
        ...

