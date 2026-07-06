import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class FindingResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    page_id: Optional[uuid.UUID]
    finding_type: str
    category: str
    severity: str
    confidence: Optional[float]
    evidence_text: Optional[str]
    explanation: Optional[str]
    bounding_box: Optional[Dict[str, Any]]
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}
