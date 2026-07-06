# app/routers/knowledge.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.rag.service import RagService
import os

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge Base"]
)

class IngestRequest(BaseModel):
    file_path: str
    doc_type: Optional[str] = "knowledge_book"

@router.post("/ingest")
async def ingest_document(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Ingest a PDF document into the global knowledge base.
    """
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    rag_service = RagService()

    # Run the chunking and embedding in the background to avoid blocking the HTTP response
    background_tasks.add_task(rag_service.index_knowledge_document, request.file_path, request.doc_type)

    return {
        "status": "processing",
        "message": f"Document {os.path.basename(request.file_path)} is being indexed in the background."
    }
