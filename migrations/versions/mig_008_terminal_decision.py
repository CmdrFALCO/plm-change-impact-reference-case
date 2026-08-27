"""MIG-008 - frozen terminal Decision persistence and append-only basis."""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "mig_008"
down_revision: str | None = "mig_007_process_history"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table("decision_records",
        sa.Column("decision_record_id", sa.String(64), primary_key=True),
        sa.Column("change_case_id", sa.String(64), nullable=False),
        sa.Column("assessment_baseline_id", sa.String(64), nullable=False),
        sa.Column("overlay_revision_id", sa.String(64), nullable=False),
        sa.Column("impact_execution_id", sa.String(64), nullable=False),
        sa.Column("required_authority_level", sa.String(32), nullable=False),
        sa.Column("current_authority_level", sa.String(32), nullable=False),
        sa.Column("outcome", sa.String(64), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("decision_authority", sa.String(255), nullable=False),
        sa.Column("decision_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("required_authority_level IN ('Standard', 'Elevated')", name="ck_decision_records_required_authority"),
        sa.CheckConstraint("current_authority_level IN ('Standard', 'Elevated')", name="ck_decision_records_current_authority"),
        sa.CheckConstraint("outcome IN ('Authorised for Downstream Processing', 'Authorised with Conditions', 'Rejected')", name="ck_decision_records_outcome"),
        sa.ForeignKeyConstraint(["change_case_id"], ["change_cases.change_case_id"]),
        sa.ForeignKeyConstraint(["assessment_baseline_id"], ["assessment_baselines.assessment_baseline_id"]),
        sa.ForeignKeyConstraint(["overlay_revision_id"], ["overlay_revisions.overlay_revision_id"]),
        sa.ForeignKeyConstraint(["impact_execution_id"], ["impact_executions.impact_execution_id"]),
    )
    op.create_index("ix_decision_records_change_case_id", "decision_records", ["change_case_id"])
    op.create_table("decision_support_assessments",
        sa.Column("decision_support_assessment_id", sa.String(64), primary_key=True),
        sa.Column("decision_record_id", sa.String(64), nullable=False),
        sa.Column("assessment_id", sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(["decision_record_id"], ["decision_records.decision_record_id"]),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.assessment_id"]),
        sa.UniqueConstraint("decision_record_id", "assessment_id", name="uq_decision_support_assessment"),
    )
    op.create_table("decision_scope_items",
        sa.Column("decision_record_id", sa.String(64), nullable=False),
        sa.Column("change_item_id", sa.String(64), nullable=False),
        sa.Column("change_item_revision", sa.String(32), nullable=False),
        sa.ForeignKeyConstraint(["decision_record_id"], ["decision_records.decision_record_id"]),
        sa.ForeignKeyConstraint(["change_item_id", "change_item_revision"], ["change_item_revisions.change_item_id", "change_item_revisions.change_item_revision"]),
        sa.PrimaryKeyConstraint("decision_record_id", "change_item_id", "change_item_revision"),
    )
    op.create_table("decision_conditions",
        sa.Column("decision_condition_id", sa.String(64), primary_key=True),
        sa.Column("decision_record_id", sa.String(64), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("responsible_downstream_role", sa.String(255), nullable=False),
        sa.Column("required_before_stage", sa.String(64), nullable=False),
        sa.Column("expected_completion_evidence", sa.Text(), nullable=False),
        sa.CheckConstraint("required_before_stage IN ('Pre-implementation', 'Pre-release', 'Post-implementation monitoring')", name="ck_decision_conditions_stage"),
        sa.ForeignKeyConstraint(["decision_record_id"], ["decision_records.decision_record_id"]),
    )
    for table in ("decision_records", "decision_support_assessments", "decision_scope_items", "decision_conditions"):
        op.execute(f"CREATE TRIGGER trg_{table}_immutable_update BEFORE UPDATE ON {table} FOR EACH ROW BEGIN SELECT RAISE(ABORT, 'Decision basis is immutable'); END")
        op.execute(f"CREATE TRIGGER trg_{table}_immutable_delete BEFORE DELETE ON {table} FOR EACH ROW BEGIN SELECT RAISE(ABORT, 'Decision basis is immutable'); END")


def downgrade() -> None:
    for table in ("decision_conditions", "decision_scope_items", "decision_support_assessments", "decision_records"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_immutable_delete")
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_immutable_update")
    op.drop_table("decision_conditions")
    op.drop_table("decision_scope_items")
    op.drop_table("decision_support_assessments")
    op.drop_index("ix_decision_records_change_case_id", table_name="decision_records")
    op.drop_table("decision_records")
