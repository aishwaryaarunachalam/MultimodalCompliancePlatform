import uuid
from datetime import datetime
from typing import Optional, List, Literal, Any
from pydantic import BaseModel, field_validator

VALID_RULE_TYPES = {"keyword", "regex", "semantic"}
VALID_SEVERITIES = {"low", "medium", "high", "critical"}


class PolicyRule(BaseModel):
    type: str
    value: str
    severity: str
    description: Optional[str] = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in VALID_RULE_TYPES:
            raise ValueError(f"type must be one of {VALID_RULE_TYPES}")
        return v

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        if v not in VALID_SEVERITIES:
            raise ValueError(f"severity must be one of {VALID_SEVERITIES}")
        return v


class PolicyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rules: List[PolicyRule] = []
    is_active: bool = True


class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[List[PolicyRule]] = None
    is_active: Optional[bool] = None


class PolicyResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    rules: List[Any]
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}
