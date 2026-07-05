# app/dependencies.py
from app.config import get_settings

def get_workflow_service():
    from app.services.workflow_service import WorkflowService
    return WorkflowService()