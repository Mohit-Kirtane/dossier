from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Enterprise Knowledge Copilot"
    cors_origins: list[str] = ["*"]

    # LLM (Google Gemini, via its OpenAI-compatible endpoint)
    llm_api_key: str = ""
    llm_api_key_fallback: str = ""
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    llm_model: str = "gemini-3.6-flash"

    # Embeddings (local, free, no API quota used)
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Storage
    database_url: str = "sqlite:///./data/app.db"
    faiss_index_dir: str = "./data/faiss_index"
    upload_dir: str = "./data/uploads"
    policy_faiss_index_dir: str = "./data/policy_faiss_index"
    policy_upload_dir: str = "./data/policy_uploads"

    # Retrieval / chunking
    chunk_size: int = 1000
    chunk_overlap: int = 150
    retrieval_k: int = 4
    relevance_score_threshold: float = 0.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
