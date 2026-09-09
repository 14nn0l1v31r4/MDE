from datetime import datetime, timedelta, timezone
from typing import Any
import jwt

from app.domain.exceptions.domain_exceptions import UnauthorizedAccessError


class PyJWTSecurityTokenService:
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        expire_minutes: int = 30,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    def create_access_token(
        self, data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        now_utc = datetime.now(timezone.utc)
        if expires_delta:
            expire = now_utc + expires_delta
        else:
            expire = now_utc + timedelta(minutes=self.expire_minutes)

        to_encode.update({
            "exp": expire,
            "iat": now_utc,
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            return payload
        except jwt.ExpiredSignatureError as e:
            raise UnauthorizedAccessError("Token expirado") from e
        except jwt.PyJWTError as e:
            raise UnauthorizedAccessError("Token inválido") from e

