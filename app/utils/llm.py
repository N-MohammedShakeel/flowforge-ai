# app/utils/llm.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import get_settings

settings = get_settings()

def get_llm(temperature: float = None):
    """Return configured LLM instance"""
    return ChatGoogleGenerativeAI(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        temperature=temperature or settings.gemini_temperature,
        max_output_tokens=2000,
    )

def get_structured_llm(model_name: str = None):
    """For structured output (Pydantic models)"""
    return ChatGoogleGenerativeAI(
        api_key=settings.gemini_api_key,
        model=model_name or settings.gemini_model,
        temperature=0.2,  # Lower temperature for structured output
    )