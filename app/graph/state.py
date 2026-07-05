from typing import TypedDict, Annotated
from operator import add
from app.models.state import ArchitectureState

class GraphState(TypedDict):
    """LangGraph internal state"""
    state: ArchitectureState
    workflow_type: str
    payload: dict
    messages: Annotated[list, add]  # For conversation history if needed