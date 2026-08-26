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
