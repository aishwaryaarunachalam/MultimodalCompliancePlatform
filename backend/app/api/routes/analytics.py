from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.db import crud

router = APIRouter()


@router.get("/dashboard")
async def dashboard(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_dashboard_stats(db, days=days)
