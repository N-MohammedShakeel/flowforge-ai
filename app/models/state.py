# app/models/state.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime

class Node(BaseModel):
    id: str = Field(..., description="Unique identifier for the node.")
    label: str = Field(..., description="Display label for the node.")
    type: str = Field(..., description="The category/type of the node (e.g., frontend, database, queue).")
    technology: str = Field(..., description="Specific technology used (e.g., React, PostgreSQL, RabbitMQ).")
    description: str = Field(..., description="A brief description of the node's role in the architecture.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the node.")

    class Config:
        extra = "allow"

class Edge(BaseModel):
    source: str = Field(..., description="ID of the source node.")
    target: str = Field(..., description="ID of the target node.")
    type: str = Field(..., description="The type of connection (e.g., api, database, event).")
    label: Optional[str] = Field(None, description="Optional label describing the connection.")

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

# ── Security & Compliance ────────────────────────────────────────────────────
class ComplianceItem(BaseModel):
    standard: str                          # e.g. "GDPR", "HIPAA", "PCI-DSS"
    requirement: str                       # what the standard demands
    status: Literal["compliant", "violation", "needs_review"]
    recommendation: str

class SecurityReport(BaseModel):
    risk_level: Literal["low", "medium", "high", "critical"] = "medium"
    compliance_items: List[ComplianceItem] = Field(default_factory=list)
    vulnerabilities: List[str] = Field(default_factory=list)
    security_recommendations: List[str] = Field(default_factory=list)
    required_nodes: List[Node] = Field(default_factory=list)   # nodes that MUST be added
    required_edges: List[Edge] = Field(default_factory=list)   # edges that MUST be added
    web_sources: List[str] = Field(default_factory=list)       # URLs searched

    class Config:
        extra = "allow"

# ── Infrastructure / DevOps ──────────────────────────────────────────────────
class InfrastructurePlan(BaseModel):
    deployment_target: str = "Docker/Kubernetes"
    infra_nodes: List[Node] = Field(default_factory=list)     # LB, CDN, registry, etc.
    infra_edges: List[Edge] = Field(default_factory=list)
    ci_cd_pipeline: List[str] = Field(default_factory=list)   # steps
    scaling_strategy: str = "Horizontal scaling with HPA"
    estimated_resources: Dict[str, str] = Field(default_factory=dict)

    class Config:
        extra = "allow"

# ── Database Design ──────────────────────────────────────────────────────────
class TableSchema(BaseModel):
    table_name: str
    columns: List[Dict[str, str]]   # [{"name": ..., "type": ..., "constraints": ...}]
    relationships: List[str] = Field(default_factory=list)

class DatabaseSchema(BaseModel):
    database_technology: str = "PostgreSQL"
    tables: List[TableSchema] = Field(default_factory=list)
    design_notes: str = ""

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

    # ── New agent outputs ────────────────────────────────────────────
    security_report: Optional[SecurityReport] = None
    infrastructure_plan: Optional[InfrastructurePlan] = None
    database_schema: Optional[DatabaseSchema] = None

    # ── Supervisor orchestration ─────────────────────────────────────
    supervisor_decision: Optional[str] = None   # next agent to call
    iteration: int = 0                          # loop guard
    max_iterations: int = 5

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