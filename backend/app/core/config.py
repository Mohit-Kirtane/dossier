from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Dossier"
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
    max_upload_size_mb: int = 5

    # Retrieval / chunking
    chunk_size: int = 1000
    chunk_overlap: int = 150
    retrieval_k: int = 4
    relevance_score_threshold: float = 0.0

    # Auth
    jwt_secret: str = "dev-secret-change-me-in-production"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    cookie_secure: bool = False  # set True in production (HTTPS)
    admin_emails: str = ""  # comma-separated; these emails get is_admin=True on signup/login

    # Google OAuth (https://console.cloud.google.com/apis/credentials)
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"

    # Tracewell (observability) - optional, no-op when unset
    tracewell_api_key: str = ""
    tracewell_base_url: str = "https://api.tracewell.dev"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_admin_emails() -> set[str]:
    settings = get_settings()
    return {e.strip().lower() for e in settings.admin_emails.split(",") if e.strip()}
