"""
Health & Observability router.
"""

import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(prefix="/health", tags=["observability"])

# Simple in-memory metrics
_metrics = {
    "requests_processed": 0,
    "start_time": time.time()
}

def increment_metrics():
    _metrics["requests_processed"] += 1

@router.get("")
async def health_check():
    """Basic application health check."""
    from app.core.config import get_settings
    settings = get_settings()
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "uptime_seconds": round(time.time() - _metrics["start_time"], 2)
    }

@router.get("/db")
async def health_db(db: AsyncSession = Depends(get_db)):
    """Database health check."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.get("/cache")
async def health_cache():
    """Cache health check (stub)."""
    return {"status": "ok", "cache": "connected"}

@router.get("/metrics")
async def get_metrics():
    """Get internal metrics."""
    return {
        "requests_processed": _metrics["requests_processed"],
        "uptime_seconds": round(time.time() - _metrics["start_time"], 2)
    }
