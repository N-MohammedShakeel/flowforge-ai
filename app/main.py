# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import workflow_router
from app.config import get_settings
import time
import logging

# ===== Logging Configuration =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("flowforge.ai")

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
    logger.debug(f"{request.method} {request.url.path} → {response.status_code} ({process_time}ms)")
    return response

# ===== Routers =====
app.include_router(workflow_router)

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
    return {
        "status": "healthy",
        "service": "flowforge-ai",
        "model": settings.openai_model
    }