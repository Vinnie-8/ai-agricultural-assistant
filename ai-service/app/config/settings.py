from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration for the AI service, loaded from environment
    variables / .env file.
    """
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    WEATHER_API_KEY: str

    KNOWLEDGE_BASE_DIR: Path = Path("knowledge_base")
    VECTOR_DB_DIR: Path = Path("vector_db")
    CHROMA_COLLECTION_NAME: str = "agri_knowledge"

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    RETRIEVER_TOP_K: int = 4

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
