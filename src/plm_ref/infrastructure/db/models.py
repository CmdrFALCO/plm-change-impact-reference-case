from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, JSON, String, Text, UniqueConstraint
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
