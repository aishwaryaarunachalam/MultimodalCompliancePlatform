import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base


class Document(Base):
    __tablename__ = "documents"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename        = Column(String, nullable=False)          # storage key
    original_name   = Column(String, nullable=False)          # user-facing name
    file_type       = Column(String, nullable=False)          # pdf | image | video
    mime_type       = Column(String, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    storage_url     = Column(String, nullable=True)           # R2 object key
    page_count      = Column(Integer, nullable=True)
    status          = Column(String, default="uploaded")      # uploaded|processing|completed|failed
    risk_level      = Column(String, default="none")          # none|low|medium|high|critical
    pii_count       = Column(Integer, default=0)
    violation_count = Column(Integer, default=0)
    error_msg       = Column(Text, nullable=True)
    uploaded_at     = Column(DateTime, default=datetime.utcnow)
    processed_at    = Column(DateTime, nullable=True)

    pages    = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    findings = relationship("Finding",      back_populates="document", cascade="all, delete-orphan")
    reviews  = relationship("Review",       back_populates="document", cascade="all, delete-orphan")
    jobs     = relationship("AnalysisJob",  back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_documents_status",     "status"),
        Index("ix_documents_risk_level", "risk_level"),
    )


class DocumentPage(Base):
    __tablename__ = "document_pages"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id    = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_num       = Column(Integer, nullable=False)
    image_url      = Column(String, nullable=True)            # R2 key for page image
    extracted_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    ocr_engine     = Column(String, nullable=True)            # tesseract|surya|gemini
    created_at     = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="pages")
    findings = relationship("Finding",  back_populates="page")

    __table_args__ = (Index("ix_document_pages_document_id", "document_id"),)


class Finding(Base):
    __tablename__ = "findings"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id  = Column(UUID(as_uuid=True), ForeignKey("documents.id",      ondelete="CASCADE"), nullable=False)
    page_id      = Column(UUID(as_uuid=True), ForeignKey("document_pages.id", ondelete="SET NULL"), nullable=True)
    finding_type = Column(String, nullable=False)             # pii | policy_violation
    category     = Column(String, nullable=False)             # pii type or policy name
    severity     = Column(String, nullable=False)             # low|medium|high|critical
    confidence   = Column(Float, nullable=True)
    evidence_text= Column(Text, nullable=True)
    explanation  = Column(Text, nullable=True)
    bounding_box = Column(JSONB, nullable=True)               # {x, y, w, h}
    status       = Column(String, default="pending")          # pending|approved|dismissed|escalated|redacted
    created_at   = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document",     back_populates="findings")
    page     = relationship("DocumentPage", back_populates="findings")
    reviews  = relationship("Review",       back_populates="finding", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_findings_document_id", "document_id"),
        Index("ix_findings_status",      "status"),
        Index("ix_findings_severity",    "severity"),
        Index("ix_findings_type",        "finding_type"),
    )


class Review(Base):
    __tablename__ = "reviews"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    finding_id  = Column(UUID(as_uuid=True), ForeignKey("findings.id",  ondelete="CASCADE"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(String, nullable=False)              # email or name (no auth for demo)
    decision    = Column(String, nullable=False)              # approve|dismiss|escalate|redact
    notes       = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    finding  = relationship("Finding",  back_populates="reviews")
    document = relationship("Document", back_populates="reviews")

    __table_args__ = (Index("ix_reviews_finding_id", "finding_id"),)


class Policy(Base):
    __tablename__ = "policies"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name        = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    rules       = Column(JSONB, default=list)                 # [{type, value, severity, description}]
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id     = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    status          = Column(String, default="queued")        # queued|processing|completed|failed
    total_pages     = Column(Integer, nullable=True)
    processed_pages = Column(Integer, default=0)
    error_msg       = Column(Text, nullable=True)
    started_at      = Column(DateTime, nullable=True)
    completed_at    = Column(DateTime, nullable=True)

    document = relationship("Document", back_populates="jobs")

    __table_args__ = (Index("ix_jobs_document_id", "document_id"),)
