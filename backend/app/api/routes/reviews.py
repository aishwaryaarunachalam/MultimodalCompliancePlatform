import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.db import crud
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter()

# Maps reviewer decision → finding status
DECISION_TO_STATUS = {
    "approve":  "approved",
    "dismiss":  "dismissed",
    "escalate": "escalated",
    "redact":   "redacted",
}


@router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(body: ReviewCreate, db: AsyncSession = Depends(get_db)):
    finding = await crud.get_finding(db, body.finding_id)
    if not finding:
        raise HTTPException(404, "Finding not found")

    new_status = DECISION_TO_STATUS[body.decision]
    await crud.update_finding_status(db, body.finding_id, new_status)

    review = await crud.create_review(
        db,
        finding_id=body.finding_id,
        document_id=finding.document_id,
        reviewer_id=body.reviewer_id,
        decision=body.decision,
        notes=body.notes,
    )

    # Recompute document risk level after decision
    await crud.recompute_document_risk(db, finding.document_id)
    await db.commit()

    return review


@router.get("", response_model=List[ReviewResponse])
async def list_reviews(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await crud.list_reviews(db, document_id)
