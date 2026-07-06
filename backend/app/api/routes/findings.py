import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.db import crud
from app.schemas.finding import FindingResponse

router = APIRouter()


@router.get("", response_model=List[FindingResponse])
async def list_findings(
    document_id:  Optional[uuid.UUID] = None,
    status:       Optional[str] = None,
    severity:     Optional[str] = None,
    finding_type: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit:  int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    return await crud.list_findings(
        db,
        document_id=document_id,
        status=status,
        severity=severity,
        finding_type=finding_type,
        offset=offset,
        limit=limit,
    )


@router.get("/{finding_id}", response_model=FindingResponse)
async def get_finding(finding_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_finding(db, finding_id)
    if not obj:
        raise HTTPException(404, "Finding not found")
    return obj
