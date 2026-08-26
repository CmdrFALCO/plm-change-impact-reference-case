from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, ConfigDict, model_validator
from sqlalchemy.orm import Session

from plm_ref.domain.payloads import (
    ApplicabilityRulePayload,
    ConfigurationContextFeatureValues,
    EffectivityPayload,
)
from plm_ref.infrastructure.db.models import (
    ConfigurationContext,
    EvidenceRecord,
    ProductElement,
    ProductStructureOccurrence,
    ProductVersion,
    Requirement,
)

DEFAULT_SHARED_SOURCE_FIXTURE = (
    Path(__file__).resolve().parents[3] / "data" / "scenarios" / "shared" / "source_state.yaml"
)


class _StrictFixtureModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class _SourceMetadata(_StrictFixtureModel):
    source_class: str
    source_identifier: str
    extraction_timestamp: datetime


class ProductElementFixture(_SourceMetadata):
    product_element_id: str
    external_identifier: str
    name: str
    element_type: str


class ProductVersionFixture(_SourceMetadata):
    product_version_id: str
    product_element_id: str
    revision: str
    iteration: str
    lifecycle_state: str
    is_baselined: bool
    supersedes_product_version_id: str | None


class ConfigurationContextFixture(_StrictFixtureModel):
    configuration_context_id: str
    name: str
    feature_values: ConfigurationContextFeatureValues
    completeness_state: str


class EffectivitySpecificationFixture(EffectivityPayload):
    effectivity_specification_id: str


class ProductStructureOccurrenceFixture(_SourceMetadata):
    occurrence_id: str
    parent_product_version_id: str
    child_product_version_id: str
    position: str
    quantity: int
    unit: str
    applicability_rule: ApplicabilityRulePayload
    effectivity_specification: EffectivityPayload


class RequirementFixture(_SourceMetadata):
    requirement_id: str
    requirement_revision: str
    text: str
    allocated_product_element_id: str


class EvidenceRecordFixture(_SourceMetadata):
    evidence_record_id: str
    evidence_type: str
    reference: str
    applicable_product_version_id: str
    configuration_context_id: str
    requirement_id: str | None
    result: str
    issue_date: date
    validity_state: str
    provider: str
    superseded_by_evidence_id: str | None


class SharedSourceFixture(_StrictFixtureModel):
    product_elements: list[ProductElementFixture]
    product_versions: list[ProductVersionFixture]
    configuration_contexts: list[ConfigurationContextFixture]
    applicability_rules: list[ApplicabilityRulePayload]
    effectivity_specifications: list[EffectivitySpecificationFixture]
    product_structure_occurrences: list[ProductStructureOccurrenceFixture]
    requirements: list[RequirementFixture]
    evidence_records: list[EvidenceRecordFixture]

    @model_validator(mode="after")
    def validate_fixture_identity_and_embedded_value_objects(self) -> Self:
        collections = (
            ("product_element_id", self.product_elements),
            ("product_version_id", self.product_versions),
            ("configuration_context_id", self.configuration_contexts),
            ("rule_id", self.applicability_rules),
            ("effectivity_specification_id", self.effectivity_specifications),
            ("occurrence_id", self.product_structure_occurrences),
            ("requirement_id", self.requirements),
            ("evidence_record_id", self.evidence_records),
        )
        for identity_field, records in collections:
            values = [getattr(record, identity_field) for record in records]
            if len(values) != len(set(values)):
                raise ValueError(f"duplicate {identity_field} in shared source fixture")

        applicability_values = {
            item.rule_id: item.model_dump(mode="json") for item in self.applicability_rules
        }
        effectivity_values = {
            tuple(
                sorted(
                    item.model_dump(
                        mode="json", exclude={"effectivity_specification_id"}
                    ).items()
                )
            )
            for item in self.effectivity_specifications
        }

        for occurrence in self.product_structure_occurrences:
            rule_payload = occurrence.applicability_rule.model_dump(mode="json")
            if applicability_values.get(occurrence.applicability_rule.rule_id) != rule_payload:
                raise ValueError(
                    f"occurrence {occurrence.occurrence_id} applicability payload does not match "
                    "the declared shared applicability rule"
                )
            effectivity_payload = tuple(
                sorted(occurrence.effectivity_specification.model_dump(mode="json").items())
            )
            if effectivity_payload not in effectivity_values:
                raise ValueError(
                    f"occurrence {occurrence.occurrence_id} effectivity payload does not match "
                    "a declared shared effectivity specification"
                )
        return self


@dataclass(frozen=True)
class SourceFixtureLoadResult:
    product_elements: int
    product_versions: int
    product_structure_occurrences: int
    configuration_contexts: int
    requirements: int
    evidence_records: int


def read_shared_source_fixture(
    fixture_path: str | Path = DEFAULT_SHARED_SOURCE_FIXTURE,
) -> SharedSourceFixture:
    path = Path(fixture_path)
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    return SharedSourceFixture.model_validate(raw)


def load_shared_source_fixture(
    session: Session,
    fixture_path: str | Path = DEFAULT_SHARED_SOURCE_FIXTURE,
) -> SourceFixtureLoadResult:
    """Validate and stage the frozen shared synthetic source projection in one transaction."""

    fixture = read_shared_source_fixture(fixture_path)

    session.add_all([ProductElement(**item.model_dump()) for item in fixture.product_elements])
    session.add_all(
        [
            ConfigurationContext(
                configuration_context_id=item.configuration_context_id,
                name=item.name,
                feature_values=item.feature_values.model_dump(mode="json"),
                completeness_state=item.completeness_state,
            )
            for item in fixture.configuration_contexts
        ]
    )
    session.flush()

    session.add_all([ProductVersion(**item.model_dump()) for item in fixture.product_versions])
    session.flush()

    session.add_all(
        [
            ProductStructureOccurrence(
                occurrence_id=item.occurrence_id,
                parent_product_version_id=item.parent_product_version_id,
                child_product_version_id=item.child_product_version_id,
                position=item.position,
                quantity=item.quantity,
                unit=item.unit,
                applicability_rule=item.applicability_rule.model_dump(mode="json"),
                effectivity_specification=item.effectivity_specification.model_dump(mode="json"),
                source_class=item.source_class,
                source_identifier=item.source_identifier,
                extraction_timestamp=item.extraction_timestamp,
            )
            for item in fixture.product_structure_occurrences
        ]
    )
    session.add_all([Requirement(**item.model_dump()) for item in fixture.requirements])
    session.flush()

    session.add_all([EvidenceRecord(**item.model_dump()) for item in fixture.evidence_records])

    # Final flush surfaces evidence FKs before returning; the caller still owns commit/rollback.
    session.flush()

    return SourceFixtureLoadResult(
        product_elements=len(fixture.product_elements),
        product_versions=len(fixture.product_versions),
        product_structure_occurrences=len(fixture.product_structure_occurrences),
        configuration_contexts=len(fixture.configuration_contexts),
        requirements=len(fixture.requirements),
        evidence_records=len(fixture.evidence_records),
    )
