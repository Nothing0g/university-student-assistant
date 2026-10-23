from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    sqlite_path: str = "storage/app.db"
    chroma_path: str = "storage/chroma"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b-instruct"
    embedding_model: str = "all-MiniLM-L6-v2"
    mock_llm: bool = True
    allow_cloud_fallback: bool = False
    api_base_url: str = "http://localhost:8000"
    max_upload_mb: int = 10
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

@lru_cache
def get_settings() -> Settings:
    return Settings()
