# app/agents/base.py
from abc import ABC, abstractmethod
from app.models.state import ArchitectureState
from app.utils.llm import get_llm, get_structured_llm
from langchain_core.prompts import ChatPromptTemplate

class BaseAgent(ABC):
    def __init__(self):
        
        self.llm = get_llm()
        self.structured_llm = get_structured_llm()

    def create_prompt(self, system_prompt: str, user_prompt: str = None):
        messages = [("system", system_prompt)]
        if user_prompt:
            messages.append(("human", user_prompt))
        return ChatPromptTemplate.from_messages(messages, template_format="mustache")

    @abstractmethod
    async def execute(self, state: ArchitectureState) -> ArchitectureState:
        pass