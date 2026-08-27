"""Frozen MIG-007 Process-history portion only.

Revision ID: mig_007_process_history
Revises: mig_007_g07_fulfilment_lock_remediation
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "mig_007_process_history"
down_revision: str | None = "mig_007_g07_fulfilment_lock_remediation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "process_history_entries",
        sa.Column("process_history_id", sa.String(64), nullable=False),
        sa.Column("change_case_id", sa.String(64), nullable=False),
        sa.Column("entry_type", sa.String(64), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actor", sa.String(255), nullable=False),
        sa.Column("origin_stage", sa.String(128), nullable=False),
        sa.Column("target_stage_or_route", sa.String(128), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("affected_change_item_id", sa.String(64), nullable=True),
        sa.Column("affected_change_item_revision", sa.String(32), nullable=True),
        sa.CheckConstraint("entry_type IN ('Returned for Information', 'Scope Revision Required', 'Additional Assessment Required', 'Escalated', 'Delegated', 'Change Item Removed from Proposal', 'Withdrawn by Change Owner')", name="ck_process_history_entries_type"),
        sa.ForeignKeyConstraint(["change_case_id"], ["change_cases.change_case_id"]),
        sa.PrimaryKeyConstraint("process_history_id"),
    )
    op.create_index("ix_process_history_entries_change_case_id", "process_history_entries", ["change_case_id"])


def downgrade() -> None:
    op.drop_index("ix_process_history_entries_change_case_id", table_name="process_history_entries")
    op.drop_table("process_history_entries")
