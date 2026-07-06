# app/models/request.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class WorkflowRequest(BaseModel):
    project_id: Optional[str] = Field(None, description="Optional ID of the project if an existing project is being updated.")
    source: str = Field("IDEA", description="Source of the architecture generation. Examples: IDEA, SRS, CODE")
    payload: Dict[str, Any] = Field(..., description="The main content for generation, such as user idea text or parsed requirements.")
    srs_file_path: Optional[str] = Field(None, description="Path to an uploaded Software Requirements Specification file if source is SRS.")
    project_zip_path: Optional[str] = Field(None, description="Path to an uploaded codebase ZIP if source is CODE.")

class ReviewRequest(BaseModel):
    project_id: str = Field(..., description="ID of the project being reviewed.")
    nodes: List[dict] = Field(..., description="Current list of nodes (components) in the architecture graph.")
    edges: List[dict] = Field(..., description="Current list of edges (connections) in the architecture graph.")
    current_review: Optional[dict] = Field(None, description="Any existing review data to build upon.")

class EnhanceRequest(BaseModel):
    project_id: str = Field(..., description="ID of the project being enhanced.")
    nodes: List[dict] = Field(..., description="Current list of nodes in the architecture graph.")
    edges: List[dict] = Field(..., description="Current list of edges in the architecture graph.")
    review: Optional[dict] = Field(None, description="Review feedback to guide the enhancement process.")