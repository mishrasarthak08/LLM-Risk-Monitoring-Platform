"""
VERITAS AI — Main FastAPI Application
Enterprise LLM Reliability, Evaluation, Observability, and Governance Platform.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from backend.app.core.config import settings
from backend.app.core.database import engine
from backend.app.models import Base
from backend.app.api.v1 import (
    auth,
    projects,
    traces,
    prompts,
    datasets,
    regressions,
    drift,
    calibration,
    audit,
    reports
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables in cloud DB on startup
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[VERITAS AI] Database schema auto-creation notice: {e}")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise LLM Reliability, Evaluation, Observability, and Governance Platform (SR 11-7 / OCC 2011-12 compliant)",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request correlation ID & timing middleware
@app.middleware("http")
async def add_process_time_and_correlation(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time-Sec"] = f"{process_time:.4f}"
    response.headers["X-Platform"] = "VERITAS-AI"
    return response


# Health Check
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "HEALTHY",
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


# Mount API V1 Routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(projects.router, prefix=settings.API_V1_PREFIX)
app.include_router(traces.router, prefix=settings.API_V1_PREFIX)
app.include_router(prompts.router, prefix=settings.API_V1_PREFIX)
app.include_router(datasets.router, prefix=settings.API_V1_PREFIX)
app.include_router(regressions.router, prefix=settings.API_V1_PREFIX)
app.include_router(drift.router, prefix=settings.API_V1_PREFIX)
app.include_router(calibration.router, prefix=settings.API_V1_PREFIX)
app.include_router(audit.router, prefix=settings.API_V1_PREFIX)
app.include_router(reports.router, prefix=settings.API_V1_PREFIX)

