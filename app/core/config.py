from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DevNexus AI Chat Board API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    environment: str = "development"
    debug: bool = True
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None
    database_url: str | None = None
    jwt_secret_key: str = "change-this-dev-secret-minimum-32-characters"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    embedding_provider: str = "ollama"
    openai_embedding_model: str = "text-embedding-3-small"
    ollama_host: str = "http://localhost:11434"
    ollama_api_key: str | None = None
    ollama_model: str = "tinyllama:latest"
    ollama_embedding_model: str = "nomic-embed-text"
    supabase_storage_bucket: str = "devnexus-files"
    max_upload_size_mb: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DEVNEXUS_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
