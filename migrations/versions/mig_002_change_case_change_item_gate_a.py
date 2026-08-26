"""MIG-002 — Change Case, Change Item, Proposal State, and Open Item.

Revision ID: mig_002
Revises: mig_001
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "mig_002"
down_revision: str | None = "mig_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "change_cases",
        sa.Column("change_case_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("trigger", sa.String(length=255), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("change_owner", sa.String(length=255), nullable=False),
        sa.Column("case_state", sa.String(length=32), nullable=False),
        sa.Column("process_iteration", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "case_state IN ('Draft', 'Open', 'In Assessment', 'Decision Ready', "
            "'Withdrawn', 'Closed by Decision')",
            name="ck_change_cases_case_state",
        ),
        sa.PrimaryKeyConstraint("change_case_id"),
    )

    op.create_table(
        "change_items",
        sa.Column("change_item_id", sa.String(length=64), nullable=False),
        sa.Column("change_case_id", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["change_case_id"], ["change_cases.change_case_id"]),
        sa.PrimaryKeyConstraint("change_item_id"),
        sa.UniqueConstraint(
            "change_item_id", "change_case_id", name="uq_change_items_identity_case"
        ),
    )

    op.create_table(
        "change_item_revisions",
        sa.Column("change_item_id", sa.String(length=64), nullable=False),
        sa.Column("change_item_revision", sa.String(length=32), nullable=False),
        sa.Column("change_case_id", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("target_type", sa.String(length=64), nullable=False),
        sa.Column("target_id", sa.String(length=64), nullable=False),
        sa.Column("current_state_reference", sa.JSON(), nullable=False),
        sa.Column("proposed_state_payload", sa.JSON(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=False),
        sa.Column("configuration_context_id", sa.String(length=64), nullable=False),
        sa.Column("intended_effectivity", sa.JSON(), nullable=False),
        sa.Column("revision_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "action IN ('Revise Product State', 'Change Applicability')",
            name="ck_change_item_revisions_action",
        ),
        sa.ForeignKeyConstraint(
            ["change_item_id", "change_case_id"],
            ["change_items.change_item_id", "change_items.change_case_id"],
            name="fk_change_item_revisions_identity_case",
        ),
        sa.ForeignKeyConstraint(
            ["configuration_context_id"],
            ["configuration_contexts.configuration_context_id"],
        ),
        sa.PrimaryKeyConstraint("change_item_id", "change_item_revision"),
        sa.UniqueConstraint(
            "change_item_id",
            "change_item_revision",
            "change_case_id",
            name="uq_change_item_revisions_identity_revision_case",
        ),
    )

    op.create_table(
        "change_item_proposal_states",
        sa.Column("change_item_id", sa.String(length=64), nullable=False),
        sa.Column("change_case_id", sa.String(length=64), nullable=False),
        sa.Column("selected_revision", sa.String(length=32), nullable=False),
        sa.Column("proposal_state", sa.String(length=32), nullable=False),
        sa.Column("state_changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state_changed_by", sa.String(length=255), nullable=False),
        sa.CheckConstraint(
            "proposal_state IN ('Active', 'Removed from Proposal')",
            name="ck_change_item_proposal_states_state",
        ),
        sa.ForeignKeyConstraint(
            ["change_item_id", "selected_revision", "change_case_id"],
            [
                "change_item_revisions.change_item_id",
                "change_item_revisions.change_item_revision",
                "change_item_revisions.change_case_id",
            ],
            name="fk_proposal_state_selected_revision_case",
        ),
        sa.PrimaryKeyConstraint("change_item_id"),
    )

    op.create_table(
        "open_items",
        sa.Column("open_item_id", sa.String(length=64), nullable=False),
        sa.Column("change_case_id", sa.String(length=64), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("item_type", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("blocking_class", sa.String(length=32), nullable=False),
        sa.Column("required_before_stage", sa.String(length=64), nullable=False),
        sa.Column("resolution_evidence_reference", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "item_type IN ('Information Gap', 'Data Defect', 'Conflict', 'Required Action')",
            name="ck_open_items_item_type",
        ),
        sa.CheckConstraint(
            "status IN ('Open', 'In Resolution', 'Resolved', 'Cancelled')",
            name="ck_open_items_status",
        ),
        sa.CheckConstraint(
            "blocking_class IN ('Blocking', 'Non-blocking')",
            name="ck_open_items_blocking_class",
        ),
        sa.CheckConstraint(
            "required_before_stage IN ('Initial Distribution', 'Assessment Completion', 'Decision')",
            name="ck_open_items_required_before_stage",
        ),
        sa.ForeignKeyConstraint(["change_case_id"], ["change_cases.change_case_id"]),
        sa.PrimaryKeyConstraint("open_item_id"),
    )


def downgrade() -> None:
    op.drop_table("open_items")
    op.drop_table("change_item_proposal_states")
    op.drop_table("change_item_revisions")
    op.drop_table("change_items")
    op.drop_table("change_cases")
