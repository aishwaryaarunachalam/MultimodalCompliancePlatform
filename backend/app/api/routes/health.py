from fastapi import APIRouter, Depends
from app.dependencies import get_db, get_redis
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    db_ok = True
    redis_ok = True
    try:
        await db.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception:
        db_ok = False
    try:
        await redis.ping()
    except Exception:
        redis_ok = False
    return {"status": "ok", "db": "ok" if db_ok else "error", "redis": "ok" if redis_ok else "error"}
