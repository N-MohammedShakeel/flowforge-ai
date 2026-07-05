from pydantic import BaseModel
from typing import List, Optional
from .state import Node, Edge, ReviewResult, ArchitectureState

class WorkflowResponse(BaseModel):
    success: bool
    message: str
    state: ArchitectureState
    execution_time: Optional[float] = None