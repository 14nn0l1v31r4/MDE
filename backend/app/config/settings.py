from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Educational Analytics API"
    api_prefix: str = "/api"
    upload_dir: str = "./storage/uploads"
    cors_origins: list[str] = ["http://localhost:5173"]
    database_url: str = "postgresql+psycopg://analytics:analytics@localhost:5432/educational_analytics"
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    max_upload_size_bytes: int = 50 * 1024 * 1024  # 50 MB

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, v: str) -> str:
        if not v or len(v) < 32:
            raise ValueError(
                "JWT_SECRET_KEY deve ser configurado via ambiente e conter pelo menos 32 caracteres."
            )
        insecure_keys = [
            "educational_analytics_super_secret_jwt_key_2026_dev_only",
            "secret",
            "changeme",
            "12345678901234567890123456789012",
        ]
        if v.lower() in insecure_keys:
            raise ValueError(
                "JWT_SECRET_KEY não pode utilizar valores conhecidos ou inseguros de desenvolvimento."
            )
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
