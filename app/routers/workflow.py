# app/routers/workflow.py
from fastapi import APIRouter, HTTPException
from app.models.request import WorkflowRequest, ReviewRequest, EnhanceRequest
from app.models.response import WorkflowResponse
from app.services.workflow_service import WorkflowService
import time
from app.utils.logger import log_info, log_error

router = APIRouter(prefix="/api/v1", tags=["workflow"])

workflow_service = WorkflowService()

@router.post("/workflow/generate", response_model=WorkflowResponse)
async def generate_architecture(request: WorkflowRequest):
    """Step 1: Generate initial architecture from idea/SRS/Project"""
    try:
        start_time = time.time()
        log_info(f"Received generate_architecture request for session {request.project_id}")
        result = await workflow_service.generate_architecture(request)
        duration = time.time() - start_time
        log_info(f"Generate architecture completed in {duration:.3f}s for session {request.project_id}")
        return WorkflowResponse(success=True, message="Architecture generated", state=result)
    except ValueError as ve:
        log_error(f"Validation error in generate_architecture: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_error(f"Unexpected error in generate_architecture: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/review", response_model=WorkflowResponse)
async def review_architecture(request: ReviewRequest):
    """Step 2: Review current architecture (called when user clicks Review button)"""
    try:
        start_time = time.time()
        log_info(f"Received review_architecture request for session {request.project_id}")
        result = await workflow_service.review_architecture(request)
        duration = time.time() - start_time
        log_info(f"Review completed in {duration:.3f}s for session {request.project_id}")
        return WorkflowResponse(success=True, message="Review completed", state=result)
    except Exception as e:
        log_error(f"Unexpected error in review_architecture: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/enhance", response_model=WorkflowResponse)
async def enhance_architecture(request: EnhanceRequest):
    """Step 3: Enhance current architecture (called when user clicks Enhance button)"""
    try:
        start_time = time.time()
        log_info(f"Received enhance_architecture request for session {request.project_id}")
        result = await workflow_service.enhance_architecture(request)
        duration = time.time() - start_time
        log_info(f"Enhancement completed in {duration:.3f}s for session {request.project_id}")
        return WorkflowResponse(success=True, message="Enhancement completed", state=result)
    except Exception as e:
        log_error(f"Unexpected error in enhance_architecture: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))