from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Postgres
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "changeme-postgres"
    POSTGRES_DB: str = "secondbrain"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:changeme-postgres@localhost:5432/secondbrain"
    )

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379/0"

    # Object storage
    STORAGE_ENDPOINT: str = "http://localhost:9000"
    STORAGE_BUCKET: str = "secondbrain"

    # JWT (secrets have no safe default)
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # LLM / embeddings / reranker (placeholders only)
    LLM_BASE_URL: str = "http://localhost:8080/v1"
    LLM_API_KEY: str = "changeme-llm-key"
    LLM_MODEL: str = "placeholder-llm"
    EMBEDDING_MODEL_KEY: str = "placeholder-embedder"
    RERANKER_MODEL_KEY: str = "placeholder-reranker"


settings = Settings()
