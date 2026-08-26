"""MIG-003 — Assessment Baseline and Product Version immutability trigger subset.

Revision ID: mig_003
Revises: mig_002
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "mig_003"
down_revision: str | None = "mig_002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "assessment_baselines",
        sa.Column("assessment_baseline_id", sa.String(length=64), nullable=False),
        sa.Column("change_case_id", sa.String(length=64), nullable=False),
        sa.Column("snapshot_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("configuration_context_id", sa.String(length=64), nullable=False),
        sa.Column("effectivity_context", sa.JSON(), nullable=False),
        sa.Column("rule_set_version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["change_case_id"], ["change_cases.change_case_id"]),
        sa.ForeignKeyConstraint(
            ["configuration_context_id"], ["configuration_contexts.configuration_context_id"]
        ),
        sa.PrimaryKeyConstraint("assessment_baseline_id"),
    )
    op.create_index(
        "ix_assessment_baselines_change_case_id",
        "assessment_baselines",
        ["change_case_id"],
        unique=False,
    )

    op.create_table(
        "baseline_members",
        sa.Column("baseline_member_id", sa.String(length=64), nullable=False),
        sa.Column("assessment_baseline_id", sa.String(length=64), nullable=False),
        sa.Column("object_type", sa.String(length=64), nullable=False),
        sa.Column("object_id", sa.String(length=64), nullable=False),
        sa.Column("object_revision_or_state_token", sa.String(length=128), nullable=False),
        sa.Column("source_identifier", sa.String(length=128), nullable=False),
        sa.Column("snapshot_payload", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["assessment_baseline_id"], ["assessment_baselines.assessment_baseline_id"]
        ),
        sa.PrimaryKeyConstraint("baseline_member_id"),
    )
    op.create_index(
        "ix_baseline_members_baseline_id",
        "baseline_members",
        ["assessment_baseline_id"],
        unique=False,
    )
    op.create_index(
        "ix_baseline_members_object_lookup",
        "baseline_members",
        ["object_type", "object_id"],
        unique=False,
    )

    op.execute(
        """
        CREATE TRIGGER trg_product_versions_baseline_update_immutable
        BEFORE UPDATE ON product_versions
        FOR EACH ROW
        WHEN EXISTS (
            SELECT 1
            FROM baseline_members bm
            WHERE bm.object_type = 'Product Version'
              AND bm.object_id = OLD.product_version_id
        )
        BEGIN
            SELECT RAISE(ABORT, 'baselined Product Version is immutable');
        END
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_product_versions_baseline_delete_immutable
        BEFORE DELETE ON product_versions
        FOR EACH ROW
        WHEN EXISTS (
            SELECT 1
            FROM baseline_members bm
            WHERE bm.object_type = 'Product Version'
              AND bm.object_id = OLD.product_version_id
        )
        BEGIN
            SELECT RAISE(ABORT, 'baselined Product Version is immutable');
        END
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_product_versions_baseline_delete_immutable")
    op.execute("DROP TRIGGER IF EXISTS trg_product_versions_baseline_update_immutable")
    op.drop_index("ix_baseline_members_object_lookup", table_name="baseline_members")
    op.drop_index("ix_baseline_members_baseline_id", table_name="baseline_members")
    op.drop_table("baseline_members")
    op.drop_index("ix_assessment_baselines_change_case_id", table_name="assessment_baselines")
    op.drop_table("assessment_baselines")
