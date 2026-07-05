from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import workflow_router
import time

from app.config import get_settings
from app.routers import workflow_router  # We'll create this soon

settings = get_settings()

app = FastAPI(
    title="FlowForge AI Service",
    description="AI Engine for FlowForge - Visual Software Architecture Designer",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include routers
app.include_router(workflow_router)

@app.get("/")
async def root():
    return {
        "message": "FlowForge AI Service is running",
        "environment": settings.environment,
        "model": settings.openai_model
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}