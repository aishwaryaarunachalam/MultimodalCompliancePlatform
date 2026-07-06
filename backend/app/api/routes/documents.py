import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.db import crud
from app.core.storage.r2_client import r2
from app.schemas.document import DocumentResponse, DocumentStatusResponse, DocumentPageResponse

router = APIRouter()


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    status:     Optional[str] = None,
    risk_level: Optional[str] = None,
    file_type:  Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit:  int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await crud.list_documents(db, status=status, risk_level=risk_level,
                                     file_type=file_type, offset=offset, limit=limit)


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    doc = await crud.get_document(db, doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


@router.get("/{doc_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    doc = await crud.get_document(db, doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    job = await crud.get_job_for_document(db, doc_id)
    return DocumentStatusResponse(
        document_id=str(doc_id),
        status=doc.status,
        job_status=job.status if job else None,
        total_pages=job.total_pages if job else None,
        processed_pages=job.processed_pages if job else None,
        risk_level=doc.risk_level,
        pii_count=doc.pii_count,
        violation_count=doc.violation_count,
    )


@router.get("/{doc_id}/pages", response_model=List[DocumentPageResponse])
async def get_document_pages(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    doc = await crud.get_document(db, doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    pages = await crud.list_pages(db, doc_id)
    result = []
    for page in pages:
        p = DocumentPageResponse.model_validate(page)
        if page.image_url:
            try:
                p.image_url = r2.get_presigned_url(page.image_url, expires=3600)
            except Exception:
                pass
        result.append(p)
    return result


@router.delete("/{doc_id}", status_code=204)
async def delete_document(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    doc = await crud.get_document(db, doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    try:
        r2.delete_object(doc.storage_url)
    except Exception:
        pass
    await crud.delete_document(db, doc_id)
