# app/utils/llm.py
#
# Provider priority: Groq → Gemini → Ollama (local)
# The first provider whose credentials/config are available will be used.
# Ollama requires no API key — it's always available as a fallback if running locally.

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from app.config import get_settings
from app.utils.logger import log_info, log_warning

settings = get_settings()


def _active_provider() -> str:
    """Determine which provider to use based on available keys."""
    if settings.groq_api_key:
        return "groq"
    elif settings.gemini_api_key:
        return "gemini"
    else:
        return "ollama"


def get_llm(temperature: float = None):
    """
    Return a configured LLM instance.

    Priority: Groq → Gemini → Ollama (local qwen, no API key needed).
    """
    provider = _active_provider()

    if provider == "groq":
        log_info("LLM provider: Groq (%s)", settings.groq_model)
        return ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=temperature or settings.groq_temperature,
        )
    elif provider == "gemini":
        log_info("LLM provider: Gemini (%s)", settings.gemini_model)
        return ChatGoogleGenerativeAI(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
            temperature=temperature or settings.gemini_temperature,
            max_output_tokens=2000,
        )
    else:
        log_warning(
            "No cloud API key found — falling back to local Ollama (%s). "
            "Make sure Ollama is running: `ollama serve`",
            settings.ollama_model,
        )
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=temperature or settings.ollama_temperature,
        )


def get_structured_llm(model_name: str = None):
    """
    Return LLM configured for structured (Pydantic / JSON mode) output.

    Priority: Groq → Gemini → Ollama (local qwen, no API key needed).
    Note: lower temperature (0.1) for more deterministic structured output.
    """
    provider = _active_provider()

    if provider == "groq":
        return ChatGroq(
            api_key=settings.groq_api_key,
            model=model_name or settings.groq_model,
            temperature=0.1,
        )
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(
            api_key=settings.gemini_api_key,
            model=model_name or settings.gemini_model,
            temperature=0.1,
        )
    else:
        log_warning(
            "Structured LLM falling back to local Ollama (%s). "
            "JSON mode reliability depends on the model version.",
            settings.ollama_model,
        )
        return ChatOllama(
            model=model_name or settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.1,
            format="json",  # Ollama native JSON mode for structured output
        )