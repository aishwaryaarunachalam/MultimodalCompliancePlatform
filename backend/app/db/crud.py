import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Document, DocumentPage, Finding, Review, Policy, AnalysisJob

SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "none": 0}


def _compute_risk_level(findings: List[Finding]) -> str:
    active = [f for f in findings if f.status in ("pending", "approved")]
    if not active:
        return "none"
    worst = max(active, key=lambda f: SEVERITY_ORDER.get(f.severity, 0))
    return worst.severity


# ── Document ──────────────────────────────────────────────────────────────────

async def create_document(db: AsyncSession, **kwargs) -> Document:
    obj = Document(**kwargs)
    db.add(obj)
    await db.flush()
    return obj


async def get_document(db: AsyncSession, doc_id: uuid.UUID) -> Optional[Document]:
    return await db.get(Document, doc_id)


async def list_documents(
    db: AsyncSession,
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    file_type: Optional[str] = None,
    offset: int = 0,
    limit: int = 20,
) -> List[Document]:
    stmt = select(Document).order_by(desc(Document.uploaded_at))
    if status:
        stmt = stmt.where(Document.status == status)
    if risk_level:
        stmt = stmt.where(Document.risk_level == risk_level)
    if file_type:
        stmt = stmt.where(Document.file_type == file_type)
    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_document(db: AsyncSession, doc_id: uuid.UUID, **kwargs) -> Optional[Document]:
    obj = await db.get(Document, doc_id)
    if not obj:
        return None
    for k, v in kwargs.items():
        setattr(obj, k, v)
    await db.flush()
    return obj


async def delete_document(db: AsyncSession, doc_id: uuid.UUID) -> bool:
    obj = await db.get(Document, doc_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.flush()
    return True


async def recompute_document_risk(db: AsyncSession, doc_id: uuid.UUID) -> str:
    result = await db.execute(select(Finding).where(Finding.document_id == doc_id))
    findings = result.scalars().all()
    risk = _compute_risk_level(findings)
    pii_count = sum(1 for f in findings if f.finding_type == "pii" and f.status != "dismissed")
    viol_count = sum(1 for f in findings if f.finding_type == "policy_violation" and f.status != "dismissed")
    await update_document(db, doc_id, risk_level=risk, pii_count=pii_count, violation_count=viol_count)
    return risk


# ── DocumentPage ──────────────────────────────────────────────────────────────

async def create_page(db: AsyncSession, **kwargs) -> DocumentPage:
    obj = DocumentPage(**kwargs)
    db.add(obj)
    await db.flush()
    return obj


async def list_pages(db: AsyncSession, doc_id: uuid.UUID) -> List[DocumentPage]:
    result = await db.execute(
        select(DocumentPage).where(DocumentPage.document_id == doc_id).order_by(DocumentPage.page_num)
    )
    return result.scalars().all()


# ── Finding ───────────────────────────────────────────────────────────────────

async def create_finding(db: AsyncSession, **kwargs) -> Finding:
    obj = Finding(**kwargs)
    db.add(obj)
    await db.flush()
    return obj


async def get_finding(db: AsyncSession, finding_id: uuid.UUID) -> Optional[Finding]:
    return await db.get(Finding, finding_id)


async def list_findings(
    db: AsyncSession,
    document_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    finding_type: Optional[str] = None,
    offset: int = 0,
    limit: int = 50,
) -> List[Finding]:
    stmt = select(Finding).order_by(
        desc(Finding.created_at)
    )
    if document_id:
        stmt = stmt.where(Finding.document_id == document_id)
    if status:
        stmt = stmt.where(Finding.status == status)
    if severity:
        stmt = stmt.where(Finding.severity == severity)
    if finding_type:
        stmt = stmt.where(Finding.finding_type == finding_type)
    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_finding_status(db: AsyncSession, finding_id: uuid.UUID, status: str) -> Optional[Finding]:
    obj = await db.get(Finding, finding_id)
    if not obj:
        return None
    obj.status = status
    await db.flush()
    return obj


# ── Review ────────────────────────────────────────────────────────────────────

async def create_review(db: AsyncSession, **kwargs) -> Review:
    obj = Review(**kwargs)
    db.add(obj)
    await db.flush()
    return obj


async def list_reviews(db: AsyncSession, document_id: uuid.UUID) -> List[Review]:
    result = await db.execute(
        select(Review).where(Review.document_id == document_id).order_by(desc(Review.reviewed_at))
    )
    return result.scalars().all()


# ── Policy ────────────────────────────────────────────────────────────────────

async def create_policy(db: AsyncSession, **kwargs) -> Policy:
    obj = Policy(**kwargs)
    db.add(obj)
    await db.flush()
    return obj


async def get_policy(db: AsyncSession, policy_id: uuid.UUID) -> Optional[Policy]:
    return await db.get(Policy, policy_id)


async def list_policies(db: AsyncSession, active_only: bool = False) -> List[Policy]:
    stmt = select(Policy).order_by(Policy.created_at)
    if active_only:
        stmt = stmt.where(Policy.is_active == True)
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_policy(db: AsyncSession, policy_id: uuid.UUID, **kwargs) -> Optional[Policy]:
    obj = await db.get(Policy, policy_id)
    if not obj:
        return None
    for k, v in kwargs.items():
        if v is not None:
            setattr(obj, k, v)
    await db.flush()
    return obj


async def delete_policy(db: AsyncSession, policy_id: uuid.UUID) -> bool:
    obj = await db.get(Policy, policy_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.flush()
    return True


# ── AnalysisJob ───────────────────────────────────────────────────────────────

async def create_job(db: AsyncSession, doc_id: uuid.UUID) -> AnalysisJob:
    obj = AnalysisJob(document_id=doc_id, started_at=datetime.utcnow())
    db.add(obj)
    await db.flush()
    return obj


async def get_job_for_document(db: AsyncSession, doc_id: uuid.UUID) -> Optional[AnalysisJob]:
    result = await db.execute(
        select(AnalysisJob).where(AnalysisJob.document_id == doc_id).order_by(desc(AnalysisJob.started_at)).limit(1)
    )
    return result.scalar_one_or_none()


async def update_job(db: AsyncSession, job_id: uuid.UUID, **kwargs) -> None:
    obj = await db.get(AnalysisJob, job_id)
    if obj:
        for k, v in kwargs.items():
            setattr(obj, k, v)
        await db.flush()


# ── Analytics ─────────────────────────────────────────────────────────────────

async def get_dashboard_stats(db: AsyncSession, days: int = 7) -> Dict[str, Any]:
    cutoff = datetime.utcnow() - timedelta(days=days)

    doc_count_result = await db.execute(
        select(func.count()).where(Document.uploaded_at >= cutoff)
    )
    total_docs = doc_count_result.scalar_one()

    finding_result = await db.execute(
        select(Finding.severity, Finding.finding_type, func.count())
        .where(Finding.created_at >= cutoff)
        .group_by(Finding.severity, Finding.finding_type)
    )
    rows = finding_result.all()

    severity_counts: Dict[str, int] = {}
    pii_total = 0
    violation_total = 0
    for severity, ftype, count in rows:
        severity_counts[severity] = severity_counts.get(severity, 0) + count
        if ftype == "pii":
            pii_total += count
        else:
            violation_total += count

    category_result = await db.execute(
        select(Finding.category, func.count())
        .where(and_(Finding.finding_type == "pii", Finding.created_at >= cutoff))
        .group_by(Finding.category)
        .order_by(desc(func.count()))
        .limit(10)
    )
    top_pii = [{"category": r[0], "count": r[1]} for r in category_result.all()]

    return {
        "period_days":      days,
        "total_documents":  total_docs,
        "total_pii":        pii_total,
        "total_violations": violation_total,
        "severity_breakdown": severity_counts,
        "top_pii_categories": top_pii,
    }
