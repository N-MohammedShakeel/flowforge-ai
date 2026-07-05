# app/routers/workflow.py
from fastapi import APIRouter, HTTPException
from app.models.request import WorkflowRequest, ReviewRequest, EnhanceRequest
from app.models.response import WorkflowResponse
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/api/v1", tags=["workflow"])

workflow_service = WorkflowService()

@router.post("/workflow/generate", response_model=WorkflowResponse)
async def generate_architecture(request: WorkflowRequest):
    """Step 1: Generate initial architecture from idea/SRS/Project"""
    try:
        result = await workflow_service.generate_architecture(request)
        return WorkflowResponse(success=True, message="Architecture generated", state=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/review", response_model=WorkflowResponse)
async def review_architecture(request: ReviewRequest):
    """Step 2: Review current architecture (called when user clicks Review button)"""
    try:
        result = await workflow_service.review_architecture(request)
        return WorkflowResponse(success=True, message="Review completed", state=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/enhance", response_model=WorkflowResponse)
async def enhance_architecture(request: EnhanceRequest):
    """Step 3: Enhance current architecture (called when user clicks Enhance button)"""
    try:
        result = await workflow_service.enhance_architecture(request)
        return WorkflowResponse(success=True, message="Enhancement completed", state=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))