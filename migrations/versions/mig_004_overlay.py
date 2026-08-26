"""MIG-004 — Overlay model and Change Item Revision lock subset.

Revision ID: mig_004
Revises: mig_003
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "mig_004"
down_revision: str | None = "mig_003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "overlay_revisions",
        sa.Column("overlay_revision_id", sa.String(length=64), nullable=False),
        sa.Column("change_case_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["change_case_id"], ["change_cases.change_case_id"]),
        sa.PrimaryKeyConstraint("overlay_revision_id"),
    )
    op.create_index(
        "ix_overlay_revisions_change_case_id",
        "overlay_revisions",
        ["change_case_id"],
        unique=False,
    )

    op.create_table(
        "overlay_change_item_memberships",
        sa.Column("overlay_revision_id", sa.String(length=64), nullable=False),
        sa.Column("change_item_id", sa.String(length=64), nullable=False),
        sa.Column("change_item_revision", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(
            ["overlay_revision_id"],
            ["overlay_revisions.overlay_revision_id"],
        ),
        sa.ForeignKeyConstraint(
            ["change_item_id", "change_item_revision"],
            [
                "change_item_revisions.change_item_id",
                "change_item_revisions.change_item_revision",
            ],
        ),
        sa.PrimaryKeyConstraint("overlay_revision_id", "change_item_id"),
        sa.UniqueConstraint(
            "overlay_revision_id",
            "change_item_id",
            "change_item_revision",
            name="uq_overlay_membership_revision",
        ),
    )
    op.create_index(
        "ix_overlay_memberships_change_item_revision",
        "overlay_change_item_memberships",
        ["change_item_id", "change_item_revision"],
        unique=False,
    )

    op.create_table(
        "overlay_local_objects",
        sa.Column("overlay_revision_id", sa.String(length=64), nullable=False),
        sa.Column("overlay_local_object_id", sa.String(length=64), nullable=False),
        sa.Column("object_type", sa.String(length=64), nullable=False),
        sa.Column("source_change_item_id", sa.String(length=64), nullable=False),
        sa.Column("source_change_item_revision", sa.String(length=32), nullable=False),
        sa.Column("state_payload", sa.JSON(), nullable=False),
        sa.CheckConstraint(
            "object_type IN ('Product Version', 'Product Structure Occurrence')",
            name="ck_overlay_local_objects_object_type",
        ),
        sa.ForeignKeyConstraint(
            [
                "overlay_revision_id",
                "source_change_item_id",
                "source_change_item_revision",
            ],
            [
                "overlay_change_item_memberships.overlay_revision_id",
                "overlay_change_item_memberships.change_item_id",
                "overlay_change_item_memberships.change_item_revision",
            ],
            name="fk_overlay_local_objects_source_membership",
        ),
        sa.PrimaryKeyConstraint("overlay_revision_id", "overlay_local_object_id"),
    )
    op.create_index(
        "ix_overlay_local_objects_source_change_item",
        "overlay_local_objects",
        ["source_change_item_id", "source_change_item_revision"],
        unique=False,
    )

    # This is the INC-04 portion of MIG-008 that can be evaluated without the
    # MIG-005 impact_executions table. Overlay row locks remain tied to first
    # execution use and are therefore installed only once that table exists.
    op.execute(
        """
        CREATE TRIGGER trg_change_item_revisions_overlay_update_immutable
        BEFORE UPDATE ON change_item_revisions
        FOR EACH ROW
        WHEN EXISTS (
            SELECT 1
            FROM overlay_change_item_memberships ocm
            WHERE ocm.change_item_id = OLD.change_item_id
              AND ocm.change_item_revision = OLD.change_item_revision
        )
        BEGIN
            SELECT RAISE(ABORT, 'used Change Item Revision is immutable');
        END
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_change_item_revisions_overlay_delete_immutable
        BEFORE DELETE ON change_item_revisions
        FOR EACH ROW
        WHEN EXISTS (
            SELECT 1
            FROM overlay_change_item_memberships ocm
            WHERE ocm.change_item_id = OLD.change_item_id
              AND ocm.change_item_revision = OLD.change_item_revision
        )
        BEGIN
            SELECT RAISE(ABORT, 'used Change Item Revision is immutable');
        END
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_change_item_revisions_overlay_delete_immutable")
    op.execute("DROP TRIGGER IF EXISTS trg_change_item_revisions_overlay_update_immutable")
    op.drop_index(
        "ix_overlay_local_objects_source_change_item",
        table_name="overlay_local_objects",
    )
    op.drop_table("overlay_local_objects")
    op.drop_index(
        "ix_overlay_memberships_change_item_revision",
        table_name="overlay_change_item_memberships",
    )
    op.drop_table("overlay_change_item_memberships")
    op.drop_index("ix_overlay_revisions_change_case_id", table_name="overlay_revisions")
    op.drop_table("overlay_revisions")
