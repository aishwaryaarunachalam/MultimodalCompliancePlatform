import uuid
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, field_validator

VALID_DECISIONS = {"approve", "dismiss", "escalate", "redact"}


class ReviewCreate(BaseModel):
    finding_id: uuid.UUID
    reviewer_id: str
    decision: str
    notes: Optional[str] = None

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v: str) -> str:
        if v not in VALID_DECISIONS:
            raise ValueError(f"decision must be one of {VALID_DECISIONS}")
        return v

    @field_validator("reviewer_id")
    @classmethod
    def validate_reviewer(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("reviewer_id cannot be empty")
        return v.strip()


class ReviewResponse(BaseModel):
    id: uuid.UUID
    finding_id: uuid.UUID
    document_id: uuid.UUID
    reviewer_id: str
    decision: str
    notes: Optional[str]
    reviewed_at: datetime
    model_config = {"from_attributes": True}
