"""MIG-001 — product/source projection.

Revision ID: mig_001
Revises: None
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "mig_001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "product_elements",
        sa.Column("product_element_id", sa.String(length=64), nullable=False),
        sa.Column("external_identifier", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("element_type", sa.String(length=32), nullable=False),
        sa.Column("source_class", sa.String(length=64), nullable=False),
        sa.Column("source_identifier", sa.String(length=128), nullable=False),
        sa.Column("extraction_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "element_type IN ('Product', 'Assembly', 'Component')",
            name="ck_product_elements_element_type",
        ),
        sa.PrimaryKeyConstraint("product_element_id"),
    )

    op.create_table(
        "configuration_contexts",
        sa.Column("configuration_context_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("feature_values", sa.JSON(), nullable=False),
        sa.Column("completeness_state", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            "completeness_state IN ('Complete', 'Partial', 'Unknown')",
            name="ck_configuration_contexts_completeness_state",
        ),
        sa.PrimaryKeyConstraint("configuration_context_id"),
    )

    op.create_table(
        "product_versions",
        sa.Column("product_version_id", sa.String(length=64), nullable=False),
        sa.Column("product_element_id", sa.String(length=64), nullable=False),
        sa.Column("revision", sa.String(length=32), nullable=False),
        sa.Column("iteration", sa.String(length=32), nullable=False),
        sa.Column("lifecycle_state", sa.String(length=64), nullable=False),
        sa.Column("is_baselined", sa.Boolean(), nullable=False),
        sa.Column("supersedes_product_version_id", sa.String(length=64), nullable=True),
        sa.Column("source_class", sa.String(length=64), nullable=False),
        sa.Column("source_identifier", sa.String(length=128), nullable=False),
        sa.Column("extraction_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_element_id"], ["product_elements.product_element_id"]
        ),
        sa.ForeignKeyConstraint(
            ["supersedes_product_version_id"], ["product_versions.product_version_id"]
        ),
        sa.PrimaryKeyConstraint("product_version_id"),
        sa.UniqueConstraint(
            "product_element_id",
            "revision",
            "iteration",
            name="uq_product_versions_element_revision_iteration",
        ),
    )

    op.create_table(
        "product_structure_occurrences",
        sa.Column("occurrence_id", sa.String(length=64), nullable=False),
        sa.Column("parent_product_version_id", sa.String(length=64), nullable=False),
        sa.Column("child_product_version_id", sa.String(length=64), nullable=False),
        sa.Column("position", sa.String(length=64), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=False),
        sa.Column("applicability_rule", sa.JSON(), nullable=False),
        sa.Column("effectivity_specification", sa.JSON(), nullable=False),
        sa.Column("source_class", sa.String(length=64), nullable=False),
        sa.Column("source_identifier", sa.String(length=128), nullable=False),
        sa.Column("extraction_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_product_version_id"], ["product_versions.product_version_id"]
        ),
        sa.ForeignKeyConstraint(
            ["child_product_version_id"], ["product_versions.product_version_id"]
        ),
        sa.PrimaryKeyConstraint("occurrence_id"),
    )

    op.create_table(
        "requirements",
        sa.Column("requirement_id", sa.String(length=64), nullable=False),
        sa.Column("requirement_revision", sa.String(length=32), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("allocated_product_element_id", sa.String(length=64), nullable=False),
        sa.Column("source_class", sa.String(length=64), nullable=False),
        sa.Column("source_identifier", sa.String(length=128), nullable=False),
        sa.Column("extraction_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["allocated_product_element_id"], ["product_elements.product_element_id"]
        ),
        sa.PrimaryKeyConstraint("requirement_id"),
    )

    op.create_table(
        "evidence_records",
        sa.Column("evidence_record_id", sa.String(length=64), nullable=False),
        sa.Column("evidence_type", sa.String(length=128), nullable=False),
        sa.Column("reference", sa.String(length=128), nullable=False),
        sa.Column("applicable_product_version_id", sa.String(length=64), nullable=False),
        sa.Column("configuration_context_id", sa.String(length=64), nullable=False),
        sa.Column("requirement_id", sa.String(length=64), nullable=True),
        sa.Column("result", sa.Text(), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("validity_state", sa.String(length=64), nullable=False),
        sa.Column("provider", sa.String(length=255), nullable=False),
        sa.Column("superseded_by_evidence_id", sa.String(length=64), nullable=True),
        sa.Column("source_class", sa.String(length=64), nullable=False),
        sa.Column("source_identifier", sa.String(length=128), nullable=False),
        sa.Column("extraction_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["applicable_product_version_id"], ["product_versions.product_version_id"]
        ),
        sa.ForeignKeyConstraint(
            ["configuration_context_id"], ["configuration_contexts.configuration_context_id"]
        ),
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.requirement_id"]),
        sa.ForeignKeyConstraint(
            ["superseded_by_evidence_id"], ["evidence_records.evidence_record_id"]
        ),
        sa.PrimaryKeyConstraint("evidence_record_id"),
    )


def downgrade() -> None:
    op.drop_table("evidence_records")
    op.drop_table("requirements")
    op.drop_table("product_structure_occurrences")
    op.drop_table("product_versions")
    op.drop_table("configuration_contexts")
    op.drop_table("product_elements")
