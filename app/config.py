# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # Gemini
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    gemini_temperature: float = 0.3

    # Environment
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000

    # File paths
    uploaded_srs_dir: str = "uploaded_files/srs"
    uploaded_projects_dir: str = "uploaded_files/projects"
    vectorstore_dir: str = "data/vectorstore"

    # Vector Store
    chroma_collection_name: str = "flowforge_knowledge"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()