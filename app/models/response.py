# app/models/response.py
from pydantic import BaseModel, Field
from typing import List, Optional
from .state import Node, Edge, ReviewResult, ArchitectureState

class WorkflowResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the workflow action was successful.")
    message: str = Field(..., description="A message describing the result of the action.")
    state: ArchitectureState = Field(..., description="The complete resulting state of the architecture after the workflow action.")
    execution_time: Optional[float] = Field(None, description="Time taken to execute the AI workflow in seconds.")