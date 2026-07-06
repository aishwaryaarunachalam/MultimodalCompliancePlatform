import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    original_name: str
    file_type: str
    mime_type: Optional[str]
    file_size_bytes: Optional[int]
    storage_url: Optional[str]
    page_count: Optional[int]
    status: str
    risk_level: str
    pii_count: int
    violation_count: int
    error_msg: Optional[str]
    uploaded_at: datetime
    processed_at: Optional[datetime]
    model_config = {"from_attributes": True}


class DocumentPageResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    page_num: int
    image_url: Optional[str]
    extracted_text: Optional[str]
    ocr_confidence: Optional[float]
    ocr_engine: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}


class DocumentStatusResponse(BaseModel):
    document_id: str
    status: str
    job_status: Optional[str]
    total_pages: Optional[int]
    processed_pages: Optional[int]
    risk_level: str
    pii_count: int
    violation_count: int
