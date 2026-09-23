from fastapi import APIRouter, HTTPException, Query, Depends
from app.services.market_insight_service import market_insight_service
from app.core.security import get_current_user

router = APIRouter()

@router.get("/market/insight", tags=["Market Intelligence"])
async def get_market_insight(query: str = Query(...), current_user=Depends(get_current_user)):
    result = market_insight_service.get_market_insight(query)
    if not result:
        raise HTTPException(status_code=503, detail="Market insight temporarily unavailable.")
    return result
