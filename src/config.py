"""Configuration management."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    anthropic_api_key: str
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    openai_api_key: str
    embedding_model: str = "text-embedding-3-small"

    pinecone_api_key: str
    pinecone_index_name: str = "lead-intelligence"
    pinecone_top_k: int = 5

    server_host: str = "0.0.0.0"
    server_port: int = 8080
    api_secret: str = ""

    ai_weight: float = 0.70
    rules_weight: float = 0.30
    hot_threshold: int = 70
    warm_threshold: int = 40

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
