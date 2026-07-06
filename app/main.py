# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import workflow_router
from app.routers.knowledge import router as knowledge_router
from app.config import get_settings
import time
from app.utils.logger import log_info, log_error

settings = get_settings()

app = FastAPI(
    title="FlowForge AI Service",
    description="AI Engine for FlowForge — Visual Software Architecture Designer",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    # In production, restrict to your Spring Boot backend URL
    allow_origins=["http://localhost:8080", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Request Timing Middleware =====
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Process-Time-Ms"] = str(process_time)
    log_info(f"{request.method} {request.url.path} → {response.status_code} ({process_time}ms)")
    return response

# ===== Routers =====
app.include_router(workflow_router)
app.include_router(knowledge_router)

# ===== Root Endpoints =====
@app.get("/")
async def root():
    return {
        "service": "FlowForge AI Service",
        "status": "running",
        "version": "0.1.0",
        "environment": settings.environment,
        "model": settings.gemini_model,
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    from app.utils.llm import _active_provider
    provider = _active_provider()
    provider_model = {
        "groq": settings.groq_model,
        "gemini": settings.gemini_model,
        "ollama": settings.ollama_model,
    }.get(provider, "unknown")
    return {
        "status": "healthy",
        "service": "flowforge-ai",
        "llm_provider": provider,
        "model": provider_model,
    }

if __name__ == "__main__":
    import uvicorn
    import sys
    import os
    # Ensure the parent directory is in the python path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)