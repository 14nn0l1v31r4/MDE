from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Educational Analytics API"
    api_prefix: str = "/api"
    upload_dir: str = "./storage/uploads"
    cors_origins: list[str] = ["http://localhost:5173"]
    database_url: str = "postgresql+psycopg://analytics:analytics@localhost:5432/educational_analytics"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
