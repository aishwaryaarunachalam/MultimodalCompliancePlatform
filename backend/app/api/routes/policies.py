import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.db import crud
from app.schemas.policy import PolicyCreate, PolicyUpdate, PolicyResponse

router = APIRouter()


@router.post("", response_model=PolicyResponse, status_code=201)
async def create_policy(body: PolicyCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_policy(
        db,
        name=body.name,
        description=body.description,
        rules=[r.model_dump() for r in body.rules],
        is_active=body.is_active,
    )


@router.get("", response_model=List[PolicyResponse])
async def list_policies(
    active_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    return await crud.list_policies(db, active_only=active_only)


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_policy(db, policy_id)
    if not obj:
        raise HTTPException(404, "Policy not found")
    return obj


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: uuid.UUID,
    body: PolicyUpdate,
    db: AsyncSession = Depends(get_db),
):
    updates = body.model_dump(exclude_none=True)
    if "rules" in updates:
        updates["rules"] = [r.model_dump() if hasattr(r, "model_dump") else r for r in updates["rules"]]
    obj = await crud.update_policy(db, policy_id, **updates)
    if not obj:
        raise HTTPException(404, "Policy not found")
    return obj


@router.delete("/{policy_id}", status_code=204)
async def delete_policy(policy_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    if not await crud.delete_policy(db, policy_id):
        raise HTTPException(404, "Policy not found")
