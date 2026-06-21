from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict, List

from app.core.database import get_db
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/demand-forecast", response_model=List[Dict[str, Any]])
async def get_demand_forecast(session: AsyncSession = Depends(get_db)):
    """Predict tomorrow's demand using historical order patterns."""
    return await AIService.get_demand_forecast(session)

@router.get("/inventory-alerts", response_model=List[Dict[str, Any]])
async def get_inventory_alerts(session: AsyncSession = Depends(get_db)):
    """Predict inventory depletion before stock-outs occur."""
    return await AIService.get_inventory_alerts(session)

@router.get("/menu-recommendations", response_model=Dict[str, Any])
async def get_menu_recommendations(session: AsyncSession = Depends(get_db)):
    """Suggest upsells and cross-sells."""
    return await AIService.get_menu_recommendations(session)

@router.get("/feedback-analysis", response_model=Dict[str, Any])
async def get_feedback_analysis(session: AsyncSession = Depends(get_db)):
    """Generate customer sentiment insights."""
    return await AIService.get_feedback_analysis(session)

@router.get("/table-recommendation", response_model=Dict[str, Any])
async def get_table_recommendation(
    guests: int = Query(..., ge=1, description="Number of guests"),
    session: AsyncSession = Depends(get_db)
):
    """Recommend the most efficient table based on party size."""
    return await AIService.get_table_recommendation(guests, session)

@router.get("/peak-hours", response_model=List[Dict[str, Any]])
async def get_peak_hours(session: AsyncSession = Depends(get_db)):
    """Predict restaurant rush periods."""
    return await AIService.get_peak_hours(session)
