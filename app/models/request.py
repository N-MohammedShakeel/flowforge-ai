# app/models/request.py
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class WorkflowRequest(BaseModel):
    project_id: Optional[str] = None
    source: str = "IDEA"
    payload: Dict[str, Any]
    srs_file_path: Optional[str] = None
    project_zip_path: Optional[str] = None

class ReviewRequest(BaseModel):
    project_id: str
    nodes: List[dict]     
    edges: List[dict]
    current_review: Optional[dict] = None

class EnhanceRequest(BaseModel):
    project_id: str
    nodes: List[dict]  
    edges: List[dict]
    review: Optional[dict] = None