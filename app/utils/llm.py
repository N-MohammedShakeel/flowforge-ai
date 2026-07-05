from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import get_settings

settings = get_settings()

def get_llm(temperature: float = None):
    """Return configured LLM instance"""
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        temperature=temperature or settings.openai_temperature,
        max_tokens=2000,
    )

def get_structured_llm(model_name: str = None):
    """For structured output (Pydantic models)"""
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=model_name or settings.openai_model,
        temperature=0.2,  # Lower temperature for structured output
    )