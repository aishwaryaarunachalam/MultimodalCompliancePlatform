"""Initial schema: documents, document_pages, findings, reviews, policies, analysis_jobs.

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id",              UUID(as_uuid=True), primary_key=True),
        sa.Column("filename",        sa.String(),  nullable=False),
        sa.Column("original_name",   sa.String(),  nullable=False),
        sa.Column("file_type",       sa.String(),  nullable=False),
        sa.Column("mime_type",       sa.String(),  nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("storage_url",     sa.String(),  nullable=True),
        sa.Column("page_count",      sa.Integer(), nullable=True),
        sa.Column("status",          sa.String(),  nullable=True),
        sa.Column("risk_level",      sa.String(),  nullable=True),
        sa.Column("pii_count",       sa.Integer(), server_default="0"),
        sa.Column("violation_count", sa.Integer(), server_default="0"),
        sa.Column("error_msg",       sa.Text(),    nullable=True),
        sa.Column("uploaded_at",     sa.DateTime(), server_default=sa.func.now()),
        sa.Column("processed_at",    sa.DateTime(), nullable=True),
    )
    op.create_index("ix_documents_status",     "documents", ["status"])
    op.create_index("ix_documents_risk_level", "documents", ["risk_level"])

    op.create_table(
        "document_pages",
        sa.Column("id",             UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id",    UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("page_num",       sa.Integer(), nullable=False),
        sa.Column("image_url",      sa.String(),  nullable=True),
        sa.Column("extracted_text", sa.Text(),    nullable=True),
        sa.Column("ocr_confidence", sa.Float(),   nullable=True),
        sa.Column("ocr_engine",     sa.String(),  nullable=True),
        sa.Column("created_at",     sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_document_pages_document_id", "document_pages", ["document_id"])

    op.create_table(
        "findings",
        sa.Column("id",            UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id",   UUID(as_uuid=True), sa.ForeignKey("documents.id",      ondelete="CASCADE"),  nullable=False),
        sa.Column("page_id",       UUID(as_uuid=True), sa.ForeignKey("document_pages.id", ondelete="SET NULL"), nullable=True),
        sa.Column("finding_type",  sa.String(),  nullable=False),
        sa.Column("category",      sa.String(),  nullable=False),
        sa.Column("severity",      sa.String(),  nullable=False),
        sa.Column("confidence",    sa.Float(),   nullable=True),
        sa.Column("evidence_text", sa.Text(),    nullable=True),
        sa.Column("explanation",   sa.Text(),    nullable=True),
        sa.Column("bounding_box",  JSONB(),      nullable=True),
        sa.Column("status",        sa.String(),  nullable=True),
        sa.Column("created_at",    sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_findings_document_id", "findings", ["document_id"])
    op.create_index("ix_findings_status",      "findings", ["status"])
    op.create_index("ix_findings_severity",    "findings", ["severity"])
    op.create_index("ix_findings_type",        "findings", ["finding_type"])

    op.create_table(
        "reviews",
        sa.Column("id",          UUID(as_uuid=True), primary_key=True),
        sa.Column("finding_id",  UUID(as_uuid=True), sa.ForeignKey("findings.id",  ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_id", sa.String(), nullable=False),
        sa.Column("decision",    sa.String(), nullable=False),
        sa.Column("notes",       sa.Text(),   nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_reviews_finding_id", "reviews", ["finding_id"])

    op.create_table(
        "policies",
        sa.Column("id",          UUID(as_uuid=True), primary_key=True),
        sa.Column("name",        sa.String(), nullable=False),
        sa.Column("description", sa.Text(),   nullable=True),
        sa.Column("rules",       JSONB(),     nullable=True),
        sa.Column("is_active",   sa.Boolean(), server_default="true"),
        sa.Column("created_at",  sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "analysis_jobs",
        sa.Column("id",              UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id",     UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status",          sa.String(),  nullable=True),
        sa.Column("total_pages",     sa.Integer(), nullable=True),
        sa.Column("processed_pages", sa.Integer(), server_default="0"),
        sa.Column("error_msg",       sa.Text(),    nullable=True),
        sa.Column("started_at",      sa.DateTime(), nullable=True),
        sa.Column("completed_at",    sa.DateTime(), nullable=True),
    )
    op.create_index("ix_jobs_document_id", "analysis_jobs", ["document_id"])


def downgrade() -> None:
    op.drop_table("analysis_jobs")
    op.drop_table("policies")
    op.drop_table("reviews")
    op.drop_table("findings")
    op.drop_table("document_pages")
    op.drop_table("documents")
