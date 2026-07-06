# app/agents/base.py
from abc import ABC, abstractmethod
from app.models.state import ArchitectureState
from app.utils.llm import get_llm, get_structured_llm
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.messages import SystemMessage, HumanMessage

class BaseAgent(ABC):
    def __init__(self):
        
        self.llm = get_llm()
        self.structured_llm = get_structured_llm()

    def create_prompt(self, system_prompt: str, user_prompt: str = None):
        messages = [SystemMessage(content=system_prompt)]
        if user_prompt:
            messages.append(HumanMessage(content=user_prompt))
        return ChatPromptTemplate.from_messages(messages)

    @abstractmethod
    async def execute(self, state: ArchitectureState) -> ArchitectureState:
        pass