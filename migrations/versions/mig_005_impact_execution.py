"""MIG-005 — Bounded impact execution, structured provenance, and first-use locks.

Revision ID: mig_005
Revises: mig_004
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "mig_005"
down_revision: str | None = "mig_004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "impact_executions",
        sa.Column("impact_execution_id", sa.String(length=64), nullable=False),
        sa.Column("change_case_id", sa.String(length=64), nullable=False),
        sa.Column("assessment_baseline_id", sa.String(length=64), nullable=False),
        sa.Column("overlay_revision_id", sa.String(length=64), nullable=False),
        sa.Column("rule_set_version", sa.String(length=64), nullable=False),
        sa.Column("execution_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("execution_status", sa.String(length=32), nullable=False),
        sa.Column("routing_status", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            "execution_status IN ('Planned', 'Running', 'Completed', 'Failed')",
            name="ck_impact_executions_execution_status",
        ),
        sa.CheckConstraint(
            "routing_status IN ('Not Started', 'Completed', 'Failed')",
            name="ck_impact_executions_routing_status",
        ),
        sa.ForeignKeyConstraint(["change_case_id"], ["change_cases.change_case_id"]),
        sa.ForeignKeyConstraint(
            ["assessment_baseline_id"],
            ["assessment_baselines.assessment_baseline_id"],
        ),
        sa.ForeignKeyConstraint(
            ["overlay_revision_id"],
            ["overlay_revisions.overlay_revision_id"],
        ),
        sa.PrimaryKeyConstraint("impact_execution_id"),
    )
    op.create_index(
        "ix_impact_executions_case_lineage",
        "impact_executions",
        ["change_case_id", "assessment_baseline_id", "overlay_revision_id"],
        unique=False,
    )

    op.create_table(
        "impact_candidates",
        sa.Column("impact_candidate_id", sa.String(length=64), nullable=False),
        sa.Column("impact_execution_id", sa.String(length=64), nullable=False),
        sa.Column("candidate_type", sa.String(length=64), nullable=False),
        sa.Column("candidate_reference", sa.String(length=64), nullable=False),
        sa.Column("affected_domain", sa.String(length=64), nullable=False),
        sa.Column("candidate_state", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            "candidate_state IN ('New', 'Assessment Planned', 'Under Assessment', "
            "'Assessed', 'Closed as Not Relevant')",
            name="ck_impact_candidates_candidate_state",
        ),
        sa.ForeignKeyConstraint(
            ["impact_execution_id"],
            ["impact_executions.impact_execution_id"],
        ),
        sa.PrimaryKeyConstraint("impact_candidate_id"),
    )
    op.create_index(
        "ix_impact_candidates_execution_id",
        "impact_candidates",
        ["impact_execution_id"],
        unique=False,
    )

    op.create_table(
        "impact_candidate_provenance",
        sa.Column(
            "impact_candidate_provenance_id",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column("impact_candidate_id", sa.String(length=64), nullable=False),
        sa.Column("change_item_id", sa.String(length=64), nullable=False),
        sa.Column("change_item_revision", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(
            ["impact_candidate_id"],
            ["impact_candidates.impact_candidate_id"],
        ),
        sa.ForeignKeyConstraint(
            ["change_item_id", "change_item_revision"],
            [
                "change_item_revisions.change_item_id",
                "change_item_revisions.change_item_revision",
            ],
        ),
        sa.PrimaryKeyConstraint("impact_candidate_provenance_id"),
    )
    op.create_index(
        "ix_impact_candidate_provenance_candidate_id",
        "impact_candidate_provenance",
        ["impact_candidate_id"],
        unique=False,
    )

    op.create_table(
        "impact_candidate_path_steps",
        sa.Column(
            "impact_candidate_provenance_id",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("source_reference", sa.String(length=64), nullable=False),
        sa.Column("relationship_type", sa.String(length=128), nullable=False),
        sa.Column("target_reference", sa.String(length=64), nullable=False),
        sa.Column("state_context", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            "sequence >= 1",
            name="ck_impact_candidate_path_steps_positive_sequence",
        ),
        sa.CheckConstraint(
            "state_context IN ('Current State', 'Proposed State')",
            name="ck_impact_candidate_path_steps_state_context",
        ),
        sa.ForeignKeyConstraint(
            ["impact_candidate_provenance_id"],
            [
                "impact_candidate_provenance.impact_candidate_provenance_id"
            ],
        ),
        sa.PrimaryKeyConstraint("impact_candidate_provenance_id", "sequence"),
    )

    _create_first_execution_use_triggers()


def _create_first_execution_use_triggers() -> None:
    trigger_definitions = {
        "trg_assessment_baselines_execution_update_immutable": """
            BEFORE UPDATE ON assessment_baselines
            FOR EACH ROW
            WHEN EXISTS (
                SELECT 1 FROM impact_executions ie
                WHERE ie.assessment_baseline_id = OLD.assessment_baseline_id
            )
            BEGIN
                SELECT RAISE(ABORT, 'used Assessment Baseline is immutable');
            END
        """,
        "trg_assessment_baselines_execution_delete_immutable": """
            BEFORE DELETE ON assessment_baselines
            FOR EACH ROW
            WHEN EXISTS (
                SELECT 1 FROM impact_executions ie
                WHERE ie.assessment_baseline_id = OLD.assessment_baseline_id
            )
            BEGIN
                SELECT RAISE(ABORT, 'used Assessment Baseline is immutable');
            END
        """,
        "trg_baseline_members_execution_insert_immutable": """
            BEFORE INSERT ON baseline_members
            FOR EACH ROW
            WHEN EXISTS (
                SELECT 1 FROM impact_executions ie
                WHERE ie.assessment_baseline_id = NEW.assessment_baseline_id
            )
            BEGIN
                SELECT RAISE(ABORT, 'used Baseline Member set is immutable');
            END
        """,
        "trg_baseline_members_execution_update_immutable": """
            BEFORE UPDATE ON baseline_members
            FOR EACH ROW
            WHEN EXISTS (
                SELECT 1 FROM impact_executions ie
                WHERE ie.assessment_baseline_id = OLD.assessment_baseline_id
                   OR ie.assessment_baseline_id = NEW.assessment_baseline_id
            )
            BEGIN
                SELECT RAISE(ABORT, 'used Baseline Member set is immutable');
            END
        """,
        "trg_baseline_members_execution_delete_immutable": """
            BEFORE DELETE ON baseline_members
            FOR EACH ROW
            WHEN EXISTS (
                SELECT 1 FROM impact_executions ie
                WHERE ie.assessment_baseline_id = OLD.assessment_baseline_id
            )
            BEGIN
                SELECT RAISE(ABORT, 'used Baseline Member set is immutable');
            END
        """,
        "trg_overlay_revisions_execution_update_immutable": """
            BEFORE UPDATE ON overlay_revisions
            FOR EACH ROW
            WHEN EXISTS (
                SELECT 1 FROM impact_executions ie
                WHERE ie.overlay_revision_id = OLD.overlay_revision_id
            )
            BEGIN
                SELECT RAISE(ABORT, 'used Overlay Revision is immutable');
            END
        """,
        "trg_overlay_revisions_execution_delete_immutable": """
            BEFORE DELETE ON overlay_revisions
            FOR EACH ROW
            WHEN EXISTS (
                SELECT 1 FROM impact_executions ie
                WHERE ie.overlay_revision_id = OLD.overlay_revision_id
            )
            BEGIN
                SELECT RAISE(ABORT, 'used Overlay Revision is immutable');
            END
        """,
        "trg_overlay_memberships_execution_insert_immutable": """
            BEFORE INSERT ON overlay_change_item_memberships
            FOR EACH ROW
            WHEN EXISTS (
                SELECT 1 FROM impact_executions ie
                WHERE ie.overlay_revision_id = NEW.overlay_revision_id
            )
            BEGIN
                SELECT RAISE(ABORT, 'used Overlay membership is immutable');
            END
        """,
        "trg_overlay_memberships_execution_update_immutable": """
            BEFORE UPDATE ON overlay_change_item_memberships
            FOR EACH ROW
            WHEN EXISTS (
                SELECT 1 FROM impact_executions ie
                WHERE ie.overlay_revision_id = OLD.overlay_revision_id
                   OR ie.overlay_revision_id = NEW.overlay_revision_id
            )
            BEGIN
                SELECT RAISE(ABORT, 'used Overlay membership is immutable');
            END
        """,
        "trg_overlay_memberships_execution_delete_immutable": """
            BEFORE DELETE ON overlay_change_item_memberships
            FOR EACH ROW
            WHEN EXISTS (
                SELECT 1 FROM impact_executions ie
                WHERE ie.overlay_revision_id = OLD.overlay_revision_id
            )
            BEGIN
                SELECT RAISE(ABORT, 'used Overlay membership is immutable');
            END
        """,
        "trg_overlay_local_objects_execution_insert_immutable": """
            BEFORE INSERT ON overlay_local_objects
            FOR EACH ROW
            WHEN EXISTS (
                SELECT 1 FROM impact_executions ie
                WHERE ie.overlay_revision_id = NEW.overlay_revision_id
            )
            BEGIN
                SELECT RAISE(ABORT, 'used Overlay-local Object set is immutable');
            END
        """,
        "trg_overlay_local_objects_execution_update_immutable": """
            BEFORE UPDATE ON overlay_local_objects
            FOR EACH ROW
            WHEN EXISTS (
                SELECT 1 FROM impact_executions ie
                WHERE ie.overlay_revision_id = OLD.overlay_revision_id
                   OR ie.overlay_revision_id = NEW.overlay_revision_id
            )
            BEGIN
                SELECT RAISE(ABORT, 'used Overlay-local Object set is immutable');
            END
        """,
        "trg_overlay_local_objects_execution_delete_immutable": """
            BEFORE DELETE ON overlay_local_objects
            FOR EACH ROW
            WHEN EXISTS (
                SELECT 1 FROM impact_executions ie
                WHERE ie.overlay_revision_id = OLD.overlay_revision_id
            )
            BEGIN
                SELECT RAISE(ABORT, 'used Overlay-local Object set is immutable');
            END
        """,
    }
    for name, body in trigger_definitions.items():
        op.execute(f"CREATE TRIGGER {name} {body}")


def downgrade() -> None:
    trigger_names = (
        "trg_overlay_local_objects_execution_delete_immutable",
        "trg_overlay_local_objects_execution_update_immutable",
        "trg_overlay_local_objects_execution_insert_immutable",
        "trg_overlay_memberships_execution_delete_immutable",
        "trg_overlay_memberships_execution_update_immutable",
        "trg_overlay_memberships_execution_insert_immutable",
        "trg_overlay_revisions_execution_delete_immutable",
        "trg_overlay_revisions_execution_update_immutable",
        "trg_baseline_members_execution_delete_immutable",
        "trg_baseline_members_execution_update_immutable",
        "trg_baseline_members_execution_insert_immutable",
        "trg_assessment_baselines_execution_delete_immutable",
        "trg_assessment_baselines_execution_update_immutable",
    )
    for name in trigger_names:
        op.execute(f"DROP TRIGGER IF EXISTS {name}")

    op.drop_table("impact_candidate_path_steps")
    op.drop_index(
        "ix_impact_candidate_provenance_candidate_id",
        table_name="impact_candidate_provenance",
    )
    op.drop_table("impact_candidate_provenance")
    op.drop_index(
        "ix_impact_candidates_execution_id",
        table_name="impact_candidates",
    )
    op.drop_table("impact_candidates")
    op.drop_index(
        "ix_impact_executions_case_lineage",
        table_name="impact_executions",
    )
    op.drop_table("impact_executions")
