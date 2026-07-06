import uuid
import magic
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.db import crud
from app.core.storage.r2_client import r2
from app.core.pipeline.analysis_pipeline import run_analysis
from app.config import settings

router = APIRouter()

ALLOWED_MIMES = {
    "application/pdf",
    "image/jpeg", "image/png", "image/webp", "image/gif",
    "video/mp4", "video/quicktime", "video/webm",
}


@router.post("")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # Size check
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(400, f"File too large ({size_mb:.1f} MB). Max: {settings.MAX_FILE_SIZE_MB} MB")

    # MIME detection
    detected_mime = magic.from_buffer(contents, mime=True)
    if detected_mime not in ALLOWED_MIMES:
        raise HTTPException(415, f"Unsupported file type: {detected_mime}")

    # Determine file_type
    if detected_mime == "application/pdf":
        file_type = "pdf"
    elif detected_mime.startswith("image/"):
        file_type = "image"
    else:
        file_type = "video"

    doc_id = uuid.uuid4()
    storage_key = f"{doc_id}/{file.filename}"

    # Upload to R2
    r2.upload_bytes(storage_key, contents, content_type=detected_mime)

    # Create DB record
    doc = await crud.create_document(
        db,
        id=doc_id,
        filename=storage_key,
        original_name=file.filename,
        file_type=file_type,
        mime_type=detected_mime,
        file_size_bytes=len(contents),
        storage_url=storage_key,
    )
    await db.commit()

    # Queue analysis
    background_tasks.add_task(run_analysis, doc_id)

    return {
        "doc_id": str(doc_id),
        "status": "uploaded",
        "original_name": file.filename,
        "file_type": file_type,
        "size_mb": round(size_mb, 2),
    }
