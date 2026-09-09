from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Educational Analytics API"
    api_prefix: str = "/api"
    upload_dir: str = "./storage/uploads"
    cors_origins: list[str] = ["http://localhost:5173"]
    database_url: str = "postgresql+psycopg://analytics:analytics@localhost:5432/educational_analytics"
    jwt_secret_key: str = "educational_analytics_super_secret_jwt_key_2026_dev_only"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    max_upload_size_bytes: int = 50 * 1024 * 1024  # 50 MB

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
