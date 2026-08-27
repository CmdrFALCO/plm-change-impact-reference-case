from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from plm_ref.infrastructure.db.base import Base


class ProductElement(Base):
    __tablename__ = "product_elements"
    __table_args__ = (
        CheckConstraint(
            "element_type IN ('Product', 'Assembly', 'Component')",
            name="ck_product_elements_element_type",
        ),
    )

    product_element_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    external_identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    element_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_class: Mapped[str] = mapped_column(String(64), nullable=False)
    source_identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    extraction_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ProductVersion(Base):
    __tablename__ = "product_versions"
    __table_args__ = (
        UniqueConstraint(
            "product_element_id",
            "revision",
            "iteration",
            name="uq_product_versions_element_revision_iteration",
        ),
    )

    product_version_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    product_element_id: Mapped[str] = mapped_column(
        ForeignKey("product_elements.product_element_id"), nullable=False
    )
    revision: Mapped[str] = mapped_column(String(32), nullable=False)
    iteration: Mapped[str] = mapped_column(String(32), nullable=False)
    lifecycle_state: Mapped[str] = mapped_column(String(64), nullable=False)
    is_baselined: Mapped[bool] = mapped_column(Boolean, nullable=False)
    supersedes_product_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("product_versions.product_version_id"), nullable=True
    )
    source_class: Mapped[str] = mapped_column(String(64), nullable=False)
    source_identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    extraction_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ProductStructureOccurrence(Base):
    __tablename__ = "product_structure_occurrences"

    occurrence_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    parent_product_version_id: Mapped[str] = mapped_column(
        ForeignKey("product_versions.product_version_id"), nullable=False
    )
    child_product_version_id: Mapped[str] = mapped_column(
        ForeignKey("product_versions.product_version_id"), nullable=False
    )
    position: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    applicability_rule: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    effectivity_specification: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    source_class: Mapped[str] = mapped_column(String(64), nullable=False)
    source_identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    extraction_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ConfigurationContext(Base):
    __tablename__ = "configuration_contexts"
    __table_args__ = (
        CheckConstraint(
            "completeness_state IN ('Complete', 'Partial', 'Unknown')",
            name="ck_configuration_contexts_completeness_state",
        ),
    )

    configuration_context_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    feature_values: Mapped[dict[str, str]] = mapped_column(JSON, nullable=False)
    completeness_state: Mapped[str] = mapped_column(String(32), nullable=False)


class Requirement(Base):
    __tablename__ = "requirements"

    requirement_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    requirement_revision: Mapped[str] = mapped_column(String(32), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    allocated_product_element_id: Mapped[str] = mapped_column(
        ForeignKey("product_elements.product_element_id"), nullable=False
    )
    source_class: Mapped[str] = mapped_column(String(64), nullable=False)
    source_identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    extraction_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"

    evidence_record_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    evidence_type: Mapped[str] = mapped_column(String(128), nullable=False)
    reference: Mapped[str] = mapped_column(String(128), nullable=False)
    applicable_product_version_id: Mapped[str] = mapped_column(
        ForeignKey("product_versions.product_version_id"), nullable=False
    )
    configuration_context_id: Mapped[str] = mapped_column(
        ForeignKey("configuration_contexts.configuration_context_id"), nullable=False
    )
    requirement_id: Mapped[str | None] = mapped_column(
        ForeignKey("requirements.requirement_id"), nullable=True
    )
    result: Mapped[str] = mapped_column(Text, nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    validity_state: Mapped[str] = mapped_column(String(64), nullable=False)
    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    superseded_by_evidence_id: Mapped[str | None] = mapped_column(
        ForeignKey("evidence_records.evidence_record_id"), nullable=True
    )
    source_class: Mapped[str] = mapped_column(String(64), nullable=False)
    source_identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    extraction_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ChangeCase(Base):
    __tablename__ = "change_cases"
    __table_args__ = (
        CheckConstraint(
            "case_state IN ('Draft', 'Open', 'In Assessment', 'Decision Ready', "
            "'Withdrawn', 'Closed by Decision')",
            name="ck_change_cases_case_state",
        ),
    )

    change_case_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    trigger: Mapped[str] = mapped_column(String(255), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    change_owner: Mapped[str] = mapped_column(String(255), nullable=False)
    case_state: Mapped[str] = mapped_column(String(32), nullable=False)
    process_iteration: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ChangeItem(Base):
    __tablename__ = "change_items"
    __table_args__ = (
        UniqueConstraint(
            "change_item_id",
            "change_case_id",
            name="uq_change_items_identity_case",
        ),
    )

    change_item_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    change_case_id: Mapped[str] = mapped_column(
        ForeignKey("change_cases.change_case_id"), nullable=False
    )


class ChangeItemRevision(Base):
    __tablename__ = "change_item_revisions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["change_item_id", "change_case_id"],
            ["change_items.change_item_id", "change_items.change_case_id"],
            name="fk_change_item_revisions_identity_case",
        ),
        UniqueConstraint(
            "change_item_id",
            "change_item_revision",
            "change_case_id",
            name="uq_change_item_revisions_identity_revision_case",
        ),
        CheckConstraint(
            "action IN ('Revise Product State', 'Change Applicability')",
            name="ck_change_item_revisions_action",
        ),
    )

    change_item_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    change_item_revision: Mapped[str] = mapped_column(String(32), primary_key=True)
    change_case_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    target_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_id: Mapped[str] = mapped_column(String(64), nullable=False)
    current_state_reference: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    proposed_state_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    configuration_context_id: Mapped[str] = mapped_column(
        ForeignKey("configuration_contexts.configuration_context_id"), nullable=False
    )
    intended_effectivity: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    revision_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ChangeItemProposalState(Base):
    __tablename__ = "change_item_proposal_states"
    __table_args__ = (
        ForeignKeyConstraint(
            ["change_item_id", "selected_revision", "change_case_id"],
            [
                "change_item_revisions.change_item_id",
                "change_item_revisions.change_item_revision",
                "change_item_revisions.change_case_id",
            ],
            name="fk_proposal_state_selected_revision_case",
        ),
        CheckConstraint(
            "proposal_state IN ('Active', 'Removed from Proposal')",
            name="ck_change_item_proposal_states_state",
        ),
    )

    change_item_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    change_case_id: Mapped[str] = mapped_column(String(64), nullable=False)
    selected_revision: Mapped[str] = mapped_column(String(32), nullable=False)
    proposal_state: Mapped[str] = mapped_column(String(32), nullable=False)
    state_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    state_changed_by: Mapped[str] = mapped_column(String(255), nullable=False)


class OpenItem(Base):
    __tablename__ = "open_items"
    __table_args__ = (
        CheckConstraint(
            "item_type IN ('Information Gap', 'Data Defect', 'Conflict', 'Required Action')",
            name="ck_open_items_item_type",
        ),
        CheckConstraint(
            "status IN ('Open', 'In Resolution', 'Resolved', 'Cancelled')",
            name="ck_open_items_status",
        ),
        CheckConstraint(
            "blocking_class IN ('Blocking', 'Non-blocking')",
            name="ck_open_items_blocking_class",
        ),
        CheckConstraint(
            "required_before_stage IN ('Initial Distribution', 'Assessment Completion', 'Decision')",
            name="ck_open_items_required_before_stage",
        ),
    )

    open_item_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    change_case_id: Mapped[str] = mapped_column(
        ForeignKey("change_cases.change_case_id"), nullable=False
    )
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)
    item_type: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    blocking_class: Mapped[str] = mapped_column(String(32), nullable=False)
    required_before_stage: Mapped[str] = mapped_column(String(64), nullable=False)
    resolution_evidence_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AssessmentBaseline(Base):
    __tablename__ = "assessment_baselines"
    __table_args__ = (
        Index("ix_assessment_baselines_change_case_id", "change_case_id"),
    )

    assessment_baseline_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    change_case_id: Mapped[str] = mapped_column(
        ForeignKey("change_cases.change_case_id"), nullable=False
    )
    snapshot_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    configuration_context_id: Mapped[str] = mapped_column(
        ForeignKey("configuration_contexts.configuration_context_id"), nullable=False
    )
    effectivity_context: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    rule_set_version: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class BaselineMember(Base):
    __tablename__ = "baseline_members"
    __table_args__ = (
        Index("ix_baseline_members_baseline_id", "assessment_baseline_id"),
        Index("ix_baseline_members_object_lookup", "object_type", "object_id"),
    )

    baseline_member_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    assessment_baseline_id: Mapped[str] = mapped_column(
        ForeignKey("assessment_baselines.assessment_baseline_id"), nullable=False
    )
    object_type: Mapped[str] = mapped_column(String(64), nullable=False)
    object_id: Mapped[str] = mapped_column(String(64), nullable=False)
    object_revision_or_state_token: Mapped[str] = mapped_column(String(128), nullable=False)
    source_identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    snapshot_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)


class OverlayRevision(Base):
    __tablename__ = "overlay_revisions"
    __table_args__ = (
        Index("ix_overlay_revisions_change_case_id", "change_case_id"),
    )

    overlay_revision_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    change_case_id: Mapped[str] = mapped_column(
        ForeignKey("change_cases.change_case_id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OverlayChangeItemMembership(Base):
    __tablename__ = "overlay_change_item_memberships"
    __table_args__ = (
        ForeignKeyConstraint(
            ["change_item_id", "change_item_revision"],
            [
                "change_item_revisions.change_item_id",
                "change_item_revisions.change_item_revision",
            ],
        ),
        UniqueConstraint(
            "overlay_revision_id",
            "change_item_id",
            "change_item_revision",
            name="uq_overlay_membership_revision",
        ),
        Index(
            "ix_overlay_memberships_change_item_revision",
            "change_item_id",
            "change_item_revision",
        ),
    )

    overlay_revision_id: Mapped[str] = mapped_column(
        ForeignKey("overlay_revisions.overlay_revision_id"), primary_key=True
    )
    change_item_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    change_item_revision: Mapped[str] = mapped_column(String(32), nullable=False)


class OverlayLocalObject(Base):
    __tablename__ = "overlay_local_objects"
    __table_args__ = (
        ForeignKeyConstraint(
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
        CheckConstraint(
            "object_type IN ('Product Version', 'Product Structure Occurrence')",
            name="ck_overlay_local_objects_object_type",
        ),
        Index(
            "ix_overlay_local_objects_source_change_item",
            "source_change_item_id",
            "source_change_item_revision",
        ),
    )

    overlay_revision_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    overlay_local_object_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    object_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_change_item_id: Mapped[str] = mapped_column(String(64), nullable=False)
    source_change_item_revision: Mapped[str] = mapped_column(String(32), nullable=False)
    state_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)


class ImpactExecution(Base):
    __tablename__ = "impact_executions"
    __table_args__ = (
        CheckConstraint(
            "execution_status IN ('Planned', 'Running', 'Completed', 'Failed')",
            name="ck_impact_executions_execution_status",
        ),
        CheckConstraint(
            "routing_status IN ('Not Started', 'Completed', 'Failed')",
            name="ck_impact_executions_routing_status",
        ),
        Index(
            "ix_impact_executions_case_lineage",
            "change_case_id",
            "assessment_baseline_id",
            "overlay_revision_id",
        ),
    )

    impact_execution_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    change_case_id: Mapped[str] = mapped_column(
        ForeignKey("change_cases.change_case_id"), nullable=False
    )
    assessment_baseline_id: Mapped[str] = mapped_column(
        ForeignKey("assessment_baselines.assessment_baseline_id"), nullable=False
    )
    overlay_revision_id: Mapped[str] = mapped_column(
        ForeignKey("overlay_revisions.overlay_revision_id"), nullable=False
    )
    rule_set_version: Mapped[str] = mapped_column(String(64), nullable=False)
    execution_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    execution_status: Mapped[str] = mapped_column(String(32), nullable=False)
    routing_status: Mapped[str] = mapped_column(String(32), nullable=False)


class ImpactCandidate(Base):
    __tablename__ = "impact_candidates"
    __table_args__ = (
        CheckConstraint(
            "candidate_state IN ('New', 'Assessment Planned', 'Under Assessment', "
            "'Assessed', 'Closed as Not Relevant')",
            name="ck_impact_candidates_candidate_state",
        ),
        Index("ix_impact_candidates_execution_id", "impact_execution_id"),
    )

    impact_candidate_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    impact_execution_id: Mapped[str] = mapped_column(
        ForeignKey("impact_executions.impact_execution_id"), nullable=False
    )
    candidate_type: Mapped[str] = mapped_column(String(64), nullable=False)
    candidate_reference: Mapped[str] = mapped_column(String(64), nullable=False)
    affected_domain: Mapped[str] = mapped_column(String(64), nullable=False)
    candidate_state: Mapped[str] = mapped_column(String(32), nullable=False)


class ImpactCandidateProvenance(Base):
    __tablename__ = "impact_candidate_provenance"
    __table_args__ = (
        ForeignKeyConstraint(
            ["change_item_id", "change_item_revision"],
            [
                "change_item_revisions.change_item_id",
                "change_item_revisions.change_item_revision",
            ],
        ),
        Index(
            "ix_impact_candidate_provenance_candidate_id",
            "impact_candidate_id",
        ),
    )

    impact_candidate_provenance_id: Mapped[str] = mapped_column(
        String(64), primary_key=True
    )
    impact_candidate_id: Mapped[str] = mapped_column(
        ForeignKey("impact_candidates.impact_candidate_id"), nullable=False
    )
    change_item_id: Mapped[str] = mapped_column(String(64), nullable=False)
    change_item_revision: Mapped[str] = mapped_column(String(32), nullable=False)


class ImpactCandidatePathStep(Base):
    __tablename__ = "impact_candidate_path_steps"
    __table_args__ = (
        CheckConstraint(
            "sequence >= 1",
            name="ck_impact_candidate_path_steps_positive_sequence",
        ),
        CheckConstraint(
            "state_context IN ('Current State', 'Proposed State')",
            name="ck_impact_candidate_path_steps_state_context",
        ),
    )

    impact_candidate_provenance_id: Mapped[str] = mapped_column(
        ForeignKey(
            "impact_candidate_provenance.impact_candidate_provenance_id"
        ),
        primary_key=True,
    )
    sequence: Mapped[int] = mapped_column(primary_key=True)
    source_reference: Mapped[str] = mapped_column(String(64), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(128), nullable=False)
    target_reference: Mapped[str] = mapped_column(String(64), nullable=False)
    state_context: Mapped[str] = mapped_column(String(32), nullable=False)


class Assessment(Base):
    __tablename__ = "assessments"
    __table_args__ = (
        CheckConstraint(
            "domain IN ('Product Engineering', 'Validation', 'Manufacturing', "
            "'Purchasing/Cost')",
            name="ck_assessments_domain",
        ),
        CheckConstraint(
            "assessment_state IN ('Planned', 'In Progress', 'Submitted', "
            "'Returned', 'Complete', 'Withdrawn')",
            name="ck_assessments_state",
        ),
        CheckConstraint(
            "relevance IN ('Relevant', 'Not Relevant', 'Undetermined')",
            name="ck_assessments_relevance",
        ),
        CheckConstraint(
            "disposition IN ('No Objection', 'No Objection with Conditions', "
            "'Objection', 'Escalation Recommended')",
            name="ck_assessments_disposition",
        ),
        Index("ix_assessments_origin_execution_id", "origin_impact_execution_id"),
    )

    assessment_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    change_case_id: Mapped[str] = mapped_column(
        ForeignKey("change_cases.change_case_id"), nullable=False
    )
    origin_impact_execution_id: Mapped[str] = mapped_column(
        ForeignKey("impact_executions.impact_execution_id"), nullable=False
    )
    domain: Mapped[str] = mapped_column(String(64), nullable=False)
    assessment_state: Mapped[str] = mapped_column(String(32), nullable=False)
    relevance: Mapped[str] = mapped_column(String(32), nullable=False)
    disposition: Mapped[str] = mapped_column(String(64), nullable=False)
    impact_statement: Mapped[str] = mapped_column(Text, nullable=False)
    assessor: Mapped[str] = mapped_column(String(255), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False)


class AssessmentObligation(Base):
    __tablename__ = "assessment_obligations"
    __table_args__ = (
        CheckConstraint(
            "domain IN ('Product Engineering', 'Validation', 'Manufacturing', "
            "'Purchasing/Cost')",
            name="ck_assessment_obligations_domain",
        ),
        CheckConstraint(
            "routing_rule_reference IN ('RRR-01', 'RRR-02', 'RRR-03', 'RRR-04')",
            name="ck_assessment_obligations_routing_rule",
        ),
        Index("ix_assessment_obligations_execution_id", "impact_execution_id"),
    )

    assessment_obligation_id: Mapped[str] = mapped_column(
        String(64), primary_key=True
    )
    impact_execution_id: Mapped[str] = mapped_column(
        ForeignKey("impact_executions.impact_execution_id"), nullable=False
    )
    impact_candidate_id: Mapped[str | None] = mapped_column(
        ForeignKey("impact_candidates.impact_candidate_id"), nullable=True
    )
    domain: Mapped[str] = mapped_column(String(64), nullable=False)
    requirement_id: Mapped[str | None] = mapped_column(
        ForeignKey("requirements.requirement_id"), nullable=True
    )
    mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False)
    fulfilled_by_assessment_id: Mapped[str | None] = mapped_column(
        ForeignKey("assessments.assessment_id"), nullable=True
    )
    routing_rule_reference: Mapped[str] = mapped_column(String(32), nullable=False)


class AssessmentImpactLink(Base):
    __tablename__ = "assessment_impact_links"

    assessment_id: Mapped[str] = mapped_column(
        ForeignKey("assessments.assessment_id"), primary_key=True
    )
    impact_candidate_id: Mapped[str] = mapped_column(
        ForeignKey("impact_candidates.impact_candidate_id"), primary_key=True
    )


class AssessmentRequirementConclusion(Base):
    __tablename__ = "assessment_requirement_conclusions"
    __table_args__ = (
        CheckConstraint(
            "conclusion IN ('Satisfied', 'Not Satisfied', 'Not Demonstrated', "
            "'Not Applicable')",
            name="ck_assessment_requirement_conclusions_value",
        ),
        UniqueConstraint(
            "assessment_id",
            "requirement_id",
            name="uq_assessment_requirement_conclusion",
        ),
    )

    assessment_requirement_conclusion_id: Mapped[str] = mapped_column(
        String(64), primary_key=True
    )
    assessment_id: Mapped[str] = mapped_column(
        ForeignKey("assessments.assessment_id"), nullable=False
    )
    requirement_id: Mapped[str] = mapped_column(
        ForeignKey("requirements.requirement_id"), nullable=False
    )
    conclusion: Mapped[str] = mapped_column(String(32), nullable=False)


class AssessmentEvidenceUse(Base):
    __tablename__ = "assessment_evidence_uses"
    __table_args__ = (
        CheckConstraint(
            "transferability_conclusion IS NULL OR "
            "transferability_conclusion IN ('Accepted as Applicable', "
            "'Partial Revalidation Required', 'Not Applicable to Proposed State')",
            name="ck_assessment_evidence_uses_transferability",
        ),
        UniqueConstraint(
            "assessment_id",
            "evidence_record_id",
            "evaluated_product_version_reference",
            name="uq_assessment_evidence_use_context",
        ),
    )

    assessment_evidence_use_id: Mapped[str] = mapped_column(
        String(64), primary_key=True
    )
    assessment_id: Mapped[str] = mapped_column(
        ForeignKey("assessments.assessment_id"), nullable=False
    )
    evidence_record_id: Mapped[str] = mapped_column(
        ForeignKey("evidence_records.evidence_record_id"), nullable=False
    )
    evaluated_product_version_reference: Mapped[str] = mapped_column(
        String(64), nullable=False
    )
    transferability_conclusion: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    evidence_state_token: Mapped[str] = mapped_column(String(128), nullable=False)
    evidence_snapshot_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False
    )


class AssessmentReuseClassification(Base):
    __tablename__ = "assessment_reuse_classifications"
    __table_args__ = (
        CheckConstraint(
            "classification IN ('Retained', 'Revalidation Required', 'Invalidated')",
            name="ck_assessment_reuse_classifications_value",
        ),
        UniqueConstraint(
            "assessment_id",
            "target_impact_execution_id",
            name="uq_assessment_reuse_target_execution",
        ),
    )

    assessment_reuse_classification_id: Mapped[str] = mapped_column(
        String(64), primary_key=True
    )
    assessment_id: Mapped[str] = mapped_column(
        ForeignKey("assessments.assessment_id"), nullable=False
    )
    target_impact_execution_id: Mapped[str] = mapped_column(
        ForeignKey("impact_executions.impact_execution_id"), nullable=False
    )
    classification: Mapped[str] = mapped_column(String(32), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)


class ProcessHistoryEntry(Base):
    __tablename__ = "process_history_entries"
    __table_args__ = (
        CheckConstraint(
            "entry_type IN ('Returned for Information', 'Scope Revision Required', "
            "'Additional Assessment Required', 'Escalated', 'Delegated', "
            "'Change Item Removed from Proposal', 'Withdrawn by Change Owner')",
            name="ck_process_history_entries_type",
        ),
        Index("ix_process_history_entries_change_case_id", "change_case_id"),
    )

    process_history_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    change_case_id: Mapped[str] = mapped_column(ForeignKey("change_cases.change_case_id"), nullable=False)
    entry_type: Mapped[str] = mapped_column(String(64), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    origin_stage: Mapped[str] = mapped_column(String(128), nullable=False)
    target_stage_or_route: Mapped[str] = mapped_column(String(128), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    affected_change_item_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    affected_change_item_revision: Mapped[str | None] = mapped_column(String(32), nullable=True)


class DecisionRecord(Base):
    __tablename__ = "decision_records"
    __table_args__ = (
        CheckConstraint("required_authority_level IN ('Standard', 'Elevated')", name="ck_decision_records_required_authority"),
        CheckConstraint("current_authority_level IN ('Standard', 'Elevated')", name="ck_decision_records_current_authority"),
        CheckConstraint("outcome IN ('Authorised for Downstream Processing', 'Authorised with Conditions', 'Rejected')", name="ck_decision_records_outcome"),
        Index("ix_decision_records_change_case_id", "change_case_id"),
    )
    decision_record_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    change_case_id: Mapped[str] = mapped_column(ForeignKey("change_cases.change_case_id"), nullable=False)
    assessment_baseline_id: Mapped[str] = mapped_column(ForeignKey("assessment_baselines.assessment_baseline_id"), nullable=False)
    overlay_revision_id: Mapped[str] = mapped_column(ForeignKey("overlay_revisions.overlay_revision_id"), nullable=False)
    impact_execution_id: Mapped[str] = mapped_column(ForeignKey("impact_executions.impact_execution_id"), nullable=False)
    required_authority_level: Mapped[str] = mapped_column(String(32), nullable=False)
    current_authority_level: Mapped[str] = mapped_column(String(32), nullable=False)
    outcome: Mapped[str] = mapped_column(String(64), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    decision_authority: Mapped[str] = mapped_column(String(255), nullable=False)
    decision_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DecisionSupportAssessment(Base):
    __tablename__ = "decision_support_assessments"
    __table_args__ = (UniqueConstraint("decision_record_id", "assessment_id", name="uq_decision_support_assessment"),)
    decision_support_assessment_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    decision_record_id: Mapped[str] = mapped_column(ForeignKey("decision_records.decision_record_id"), nullable=False)
    assessment_id: Mapped[str] = mapped_column(ForeignKey("assessments.assessment_id"), nullable=False)


class DecisionScopeItem(Base):
    __tablename__ = "decision_scope_items"
    decision_record_id: Mapped[str] = mapped_column(ForeignKey("decision_records.decision_record_id"), primary_key=True)
    change_item_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    change_item_revision: Mapped[str] = mapped_column(String(32), primary_key=True)


class DecisionCondition(Base):
    __tablename__ = "decision_conditions"
    __table_args__ = (CheckConstraint("required_before_stage IN ('Pre-implementation', 'Pre-release', 'Post-implementation monitoring')", name="ck_decision_conditions_stage"),)
    decision_condition_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    decision_record_id: Mapped[str] = mapped_column(ForeignKey("decision_records.decision_record_id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    responsible_downstream_role: Mapped[str] = mapped_column(String(255), nullable=False)
    required_before_stage: Mapped[str] = mapped_column(String(64), nullable=False)
    expected_completion_evidence: Mapped[str] = mapped_column(Text, nullable=False)
