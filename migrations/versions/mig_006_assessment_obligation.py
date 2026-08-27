"""MIG-006 - Assessment and obligation persistence boundary.

Revision ID: mig_006
Revises: mig_005
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "mig_006"
down_revision: str | None = "mig_005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "assessments",
        sa.Column("assessment_id", sa.String(length=64), nullable=False),
        sa.Column("change_case_id", sa.String(length=64), nullable=False),
        sa.Column("origin_impact_execution_id", sa.String(length=64), nullable=False),
        sa.Column("domain", sa.String(length=64), nullable=False),
        sa.Column("assessment_state", sa.String(length=32), nullable=False),
        sa.Column("relevance", sa.String(length=32), nullable=False),
        sa.Column("disposition", sa.String(length=64), nullable=False),
        sa.Column("impact_statement", sa.Text(), nullable=False),
        sa.Column("assessor", sa.String(length=255), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_locked", sa.Boolean(), nullable=False),
        sa.CheckConstraint(
            "domain IN ('Product Engineering', 'Validation', 'Manufacturing', "
            "'Purchasing/Cost')",
            name="ck_assessments_domain",
        ),
        sa.CheckConstraint(
            "assessment_state IN ('Planned', 'In Progress', 'Submitted', "
            "'Returned', 'Complete', 'Withdrawn')",
            name="ck_assessments_state",
        ),
        sa.CheckConstraint(
            "relevance IN ('Relevant', 'Not Relevant', 'Undetermined')",
            name="ck_assessments_relevance",
        ),
        sa.CheckConstraint(
            "disposition IN ('No Objection', 'No Objection with Conditions', "
            "'Objection', 'Escalation Recommended')",
            name="ck_assessments_disposition",
        ),
        sa.ForeignKeyConstraint(["change_case_id"], ["change_cases.change_case_id"]),
        sa.ForeignKeyConstraint(
            ["origin_impact_execution_id"],
            ["impact_executions.impact_execution_id"],
        ),
        sa.PrimaryKeyConstraint("assessment_id"),
    )
    op.create_index(
        "ix_assessments_origin_execution_id",
        "assessments",
        ["origin_impact_execution_id"],
        unique=False,
    )

    op.create_table(
        "assessment_obligations",
        sa.Column("assessment_obligation_id", sa.String(length=64), nullable=False),
        sa.Column("impact_execution_id", sa.String(length=64), nullable=False),
        sa.Column("impact_candidate_id", sa.String(length=64), nullable=True),
        sa.Column("domain", sa.String(length=64), nullable=False),
        sa.Column("requirement_id", sa.String(length=64), nullable=True),
        sa.Column("mandatory", sa.Boolean(), nullable=False),
        sa.Column("fulfilled_by_assessment_id", sa.String(length=64), nullable=True),
        sa.Column("routing_rule_reference", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            "domain IN ('Product Engineering', 'Validation', 'Manufacturing', "
            "'Purchasing/Cost')",
            name="ck_assessment_obligations_domain",
        ),
        sa.CheckConstraint(
            "routing_rule_reference IN ('RRR-01', 'RRR-02', 'RRR-03', 'RRR-04')",
            name="ck_assessment_obligations_routing_rule",
        ),
        sa.ForeignKeyConstraint(
            ["impact_execution_id"],
            ["impact_executions.impact_execution_id"],
        ),
        sa.ForeignKeyConstraint(
            ["impact_candidate_id"],
            ["impact_candidates.impact_candidate_id"],
        ),
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.requirement_id"]),
        sa.ForeignKeyConstraint(
            ["fulfilled_by_assessment_id"],
            ["assessments.assessment_id"],
        ),
        sa.PrimaryKeyConstraint("assessment_obligation_id"),
    )
    op.create_index(
        "ix_assessment_obligations_execution_id",
        "assessment_obligations",
        ["impact_execution_id"],
        unique=False,
    )

    op.create_table(
        "assessment_impact_links",
        sa.Column("assessment_id", sa.String(length=64), nullable=False),
        sa.Column("impact_candidate_id", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.assessment_id"]),
        sa.ForeignKeyConstraint(
            ["impact_candidate_id"],
            ["impact_candidates.impact_candidate_id"],
        ),
        sa.PrimaryKeyConstraint("assessment_id", "impact_candidate_id"),
    )

    op.create_table(
        "assessment_requirement_conclusions",
        sa.Column(
            "assessment_requirement_conclusion_id",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column("assessment_id", sa.String(length=64), nullable=False),
        sa.Column("requirement_id", sa.String(length=64), nullable=False),
        sa.Column("conclusion", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            "conclusion IN ('Satisfied', 'Not Satisfied', 'Not Demonstrated', "
            "'Not Applicable')",
            name="ck_assessment_requirement_conclusions_value",
        ),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.assessment_id"]),
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.requirement_id"]),
        sa.PrimaryKeyConstraint("assessment_requirement_conclusion_id"),
        sa.UniqueConstraint(
            "assessment_id",
            "requirement_id",
            name="uq_assessment_requirement_conclusion",
        ),
    )

    op.create_table(
        "assessment_evidence_uses",
        sa.Column("assessment_evidence_use_id", sa.String(length=64), nullable=False),
        sa.Column("assessment_id", sa.String(length=64), nullable=False),
        sa.Column("evidence_record_id", sa.String(length=64), nullable=False),
        sa.Column(
            "evaluated_product_version_reference",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column("transferability_conclusion", sa.String(length=64), nullable=True),
        sa.Column("evidence_state_token", sa.String(length=128), nullable=False),
        sa.Column("evidence_snapshot_payload", sa.JSON(), nullable=False),
        sa.CheckConstraint(
            "transferability_conclusion IS NULL OR "
            "transferability_conclusion IN ('Accepted as Applicable', "
            "'Partial Revalidation Required', 'Not Applicable to Proposed State')",
            name="ck_assessment_evidence_uses_transferability",
        ),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.assessment_id"]),
        sa.ForeignKeyConstraint(
            ["evidence_record_id"],
            ["evidence_records.evidence_record_id"],
        ),
        sa.PrimaryKeyConstraint("assessment_evidence_use_id"),
        sa.UniqueConstraint(
            "assessment_id",
            "evidence_record_id",
            "evaluated_product_version_reference",
            name="uq_assessment_evidence_use_context",
        ),
    )

    op.create_table(
        "assessment_reuse_classifications",
        sa.Column(
            "assessment_reuse_classification_id",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column("assessment_id", sa.String(length=64), nullable=False),
        sa.Column("target_impact_execution_id", sa.String(length=64), nullable=False),
        sa.Column("classification", sa.String(length=32), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "classification IN ('Retained', 'Revalidation Required', 'Invalidated')",
            name="ck_assessment_reuse_classifications_value",
        ),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.assessment_id"]),
        sa.ForeignKeyConstraint(
            ["target_impact_execution_id"],
            ["impact_executions.impact_execution_id"],
        ),
        sa.PrimaryKeyConstraint("assessment_reuse_classification_id"),
        sa.UniqueConstraint(
            "assessment_id",
            "target_impact_execution_id",
            name="uq_assessment_reuse_target_execution",
        ),
    )


def downgrade() -> None:
    op.drop_table("assessment_reuse_classifications")
    op.drop_table("assessment_evidence_uses")
    op.drop_table("assessment_requirement_conclusions")
    op.drop_table("assessment_impact_links")
    op.drop_index(
        "ix_assessment_obligations_execution_id",
        table_name="assessment_obligations",
    )
    op.drop_table("assessment_obligations")
    op.drop_index(
        "ix_assessments_origin_execution_id",
        table_name="assessments",
    )
    op.drop_table("assessments")
