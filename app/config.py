# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # LLM API Keys
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    
    # Models
    gemini_model: str = "gemini-2.5-flash"
    groq_model: str = "llama-3.1-8b-instant"
    ollama_model: str = "qwen"
    ollama_base_url: str = "http://localhost:11434"
    gemini_temperature: float = 0.3
    groq_temperature: float = 0.3
    ollama_temperature: float = 0.3

    # Environment
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000

    # File paths
    uploaded_srs_dir: str = "uploaded_files/srs"
    uploaded_projects_dir: str = "uploaded_files/projects"
    
    # RAG Settings
    vectorstore_dir: str = "data/vectorstore"
    chroma_collection_name: str = "flowforge-knowledge"

    # LangSmith
    langsmith_tracing: str = "true"
    langsmith_project: str = "FlowForge"

    # Tavily Web Search (optional — set to enable SecurityAgent web search)
    tavily_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()