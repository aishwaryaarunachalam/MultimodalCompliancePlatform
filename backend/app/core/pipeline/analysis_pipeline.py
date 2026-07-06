import uuid
import asyncio
from datetime import datetime
from typing import List

from app.db.session import AsyncSessionLocal
from app.db import crud
from app.core.processors.file_router import route_file
from app.core.ocr.ocr_router import extract_text
from app.core.analyzers.vlm_analyzer import VLMAnalyzer
from app.core.analyzers.pii_detector import PIIDetector
from app.core.analyzers.policy_checker import PolicyChecker
from app.core.storage.r2_client import r2

SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1}


async def run_analysis(doc_id: uuid.UUID) -> None:
    """
    Full multimodal analysis pipeline for a document.
    Called as a FastAPI BackgroundTask after upload.

    Steps:
      1. Download file from R2
      2. Route to processor → pages/frames
      3. For each page: OCR → PII → Policy
      4. Persist findings, update document risk level
    """
    vlm = VLMAnalyzer()
    pii_detector = PIIDetector()
    policy_checker = PolicyChecker()

    async with AsyncSessionLocal() as db:
        try:
            doc = await crud.get_document(db, doc_id)
            if not doc:
                return

            job = await crud.create_job(db, doc_id)
            await crud.update_document(db, doc_id, status="processing")
            await db.commit()

            # Download file bytes from R2
            file_bytes = r2.download_bytes(doc.storage_url)

            # Detect file type and extract pages
            pages = route_file(doc.mime_type or "application/octet-stream", file_bytes)

            # Load active policies once
            policies_orm = await crud.list_policies(db, active_only=True)
            policies = [
                {"id": str(p.id), "name": p.name, "rules": p.rules or []}
                for p in policies_orm
            ]

            await crud.update_job(db, job.id, total_pages=len(pages), status="processing")
            await db.commit()

            for page in pages:
                # OCR
                text, ocr_conf, ocr_engine = await extract_text(page.image_bytes, vlm)

                # Upload page image to R2
                page_key = f"{doc_id}/pages/page_{page.page_num}.jpg"
                r2.upload_bytes(page_key, page.image_bytes, content_type="image/jpeg")

                # Persist page record
                page_record = await crud.create_page(
                    db,
                    document_id=doc_id,
                    page_num=page.page_num,
                    image_url=page_key,
                    extracted_text=text,
                    ocr_confidence=ocr_conf,
                    ocr_engine=ocr_engine,
                )
                await db.commit()

                # PII Detection
                pii_findings = await pii_detector.run_full(page.image_bytes, text, vlm)
                for pf in pii_findings:
                    await crud.create_finding(
                        db,
                        document_id=doc_id,
                        page_id=page_record.id,
                        finding_type="pii",
                        category=pf.pii_type,
                        severity=pf.severity,
                        confidence=pf.confidence,
                        evidence_text=pf.evidence,
                        explanation=pf.explanation,
                    )

                # Policy Violation Detection
                policy_findings = await policy_checker.run_full(
                    page.image_bytes, text, policies, vlm
                )
                for vf in policy_findings:
                    await crud.create_finding(
                        db,
                        document_id=doc_id,
                        page_id=page_record.id,
                        finding_type="policy_violation",
                        category=vf.policy_name,
                        severity=vf.severity,
                        confidence=vf.confidence,
                        evidence_text=vf.violated_text,
                        explanation=vf.explanation,
                    )

                # Update job progress
                await crud.update_job(
                    db, job.id,
                    processed_pages=page.page_num,
                )
                await db.commit()

            # Final document update
            risk = await crud.recompute_document_risk(db, doc_id)
            await crud.update_document(
                db, doc_id,
                status="completed",
                page_count=len(pages),
                processed_at=datetime.utcnow(),
            )
            await crud.update_job(
                db, job.id,
                status="completed",
                completed_at=datetime.utcnow(),
            )
            await db.commit()

        except Exception as exc:
            async with AsyncSessionLocal() as err_db:
                await crud.update_document(err_db, doc_id, status="failed", error_msg=str(exc))
                job_obj = await crud.get_job_for_document(err_db, doc_id)
                if job_obj:
                    await crud.update_job(
                        err_db, job_obj.id,
                        status="failed",
                        error_msg=str(exc),
                        completed_at=datetime.utcnow(),
                    )
                await err_db.commit()
