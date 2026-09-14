
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI-Powered Vehicle Service Centre Knowledge and Booking Assistant"
    app_version: str = "1.0.0"
    app_environment: str = "development"
    debug: bool = True

    host: str = "127.0.0.1"
    port: int = 8000

    database_url: str

    secret_key: str
    access_token_expire_minutes: int = 30

    # Embedding configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    embedding_batch_size: int = 32

    # Retrieval configuration
    retrieval_top_k: int = 5
    retrieval_similarity_threshold: float = 0.30

    # LLM configuration
    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"
    llm_provider: str = "groq"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

class Settings(BaseSettings):
    # Existing settings
    app_name: str
    app_version: str
    app_environment: str
    debug: bool
    host: str
    port: int
    database_url: str

    # Step 13
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    embedding_batch_size: int = 32

    retrieval_top_k: int = 5
    retrieval_similarity_threshold: float = 0.30

   
    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"
    llm_provider: str = "groq"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    embedding_batch_size: int = 32

    retrieval_top_k: int = 5
    retrieval_similarity_threshold: float = 0.30
    

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )