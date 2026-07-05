from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class Node(BaseModel):
    id: str
    label: str
    type: str
    technology: str
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"

class Edge(BaseModel):
    source: str
    target: str
    type: str
    label: Optional[str] = None

    class Config:
        extra = "allow"

class Requirements(BaseModel):
    project_name: str = Field(default="Untitled Project")
    description: str = Field(...)
    actors: List[str] = Field(default_factory=list)
    modules: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    non_functional: List[str] = Field(default_factory=list)
    tech_preferences: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        extra = "allow"

class ReviewResult(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    architecture_score: int = Field(..., ge=0, le=100)
    scalability: int = Field(..., ge=0, le=100)
    maintainability: int = Field(..., ge=0, le=100)
    security: int = Field(..., ge=0, le=100)
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

class Enhancement(BaseModel):
    reason: str
    priority: str = Field(..., pattern="^(High|Medium|Low)$")
    node: Optional[Node] = None
    edge: Optional[Edge] = None

    class Config:
        extra = "allow"

class ArchitectureOutput(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    summary: str

    class Config:
        extra = "allow"

class ArchitectureState(BaseModel):
    project_id: Optional[str] = None
    source: str = "IDEA"
    user_input: Optional[str] = None
    requirements: Optional[Requirements] = None
    rag_context: Optional[str] = None
    project_context: Optional[str] = None
    
    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    
    review: Optional[ReviewResult] = None
    enhancements: List[Enhancement] = Field(default_factory=list)
    
    status: str = "COMPLETED"
    confidence: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        extra = "allow"

class EnhancedArchitectureOutput(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    summary: str
    changes_summary: str = "Improved architecture with better scalability and security"

    class Config:
        extra = "allow"