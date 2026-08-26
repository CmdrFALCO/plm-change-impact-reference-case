from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from plm_ref.domain.payloads import (
    BaselineApplicabilityRuleSnapshot,
    BaselineConfigurationContextSnapshot,
    BaselineOccurrenceSnapshot,
    BaselineProductVersionSnapshot,
    BaselineRequirementSnapshot,
    EffectivityPayload,
)
from plm_ref.infrastructure.db.models import (
    AssessmentBaseline,
    BaselineMember,
    ConfigurationContext,
    ProductStructureOccurrence,
    ProductVersion,
    Requirement,
)

_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BASELINE_SNAPSHOT_FIXTURE = _ROOT / "data" / "scenarios" / "shared" / "baseline_snapshots.yaml"
DEFAULT_BASELINE_FIXTURES = {
    "A": _ROOT / "data" / "scenarios" / "scenario_a" / "baseline.yaml",
    "B": _ROOT / "data" / "scenarios" / "scenario_b" / "baseline.yaml",
    "C": _ROOT / "data" / "scenarios" / "scenario_c" / "baseline.yaml",
}

BaselineObjectType = Literal[
    "Product Version",
    "Product Structure Occurrence",
    "Configuration Context",
    "Applicability Rule",
    "Effectivity Specification",
    "Requirement",
]


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AssessmentBaselineInput(_StrictModel):
    assessment_baseline_id: str
    change_case_id: str
    snapshot_timestamp: datetime
    configuration_context_id: str
    effectivity_context: EffectivityPayload
    rule_set_version: Literal["RRR-v0.1"]
    created_at: datetime


class BaselineMemberInput(_StrictModel):
    baseline_member_id: str
    assessment_baseline_id: str
    object_type: BaselineObjectType
    object_id: str
    object_revision_or_state_token: str
    source_identifier: str
    snapshot_payload: dict[str, Any]


class BaselineReuseInputs(_StrictModel):
    authoritative_current_state_unchanged: bool
    baseline_scope_still_sufficient: bool
    configuration_context_still_valid: bool
    effectivity_context_still_valid: bool
    extraction_basis_still_accepted: bool


class _CanonicalSnapshotDefinition(_StrictModel):
    object_type: BaselineObjectType
    object_id: str
    snapshot_payload: dict[str, Any]


class _BaselineMemberFixture(_StrictModel):
    baseline_member_id: str
    object_type: BaselineObjectType
    object_id: str
    object_revision_or_state_token: str
    source_identifier: str
    snapshot_alias: str


class _BaselineFixture(_StrictModel):
    assessment_baseline_id: str
    change_case_id: str
    snapshot_timestamp: datetime
    configuration_context_id: str
    effectivity_context: EffectivityPayload
    rule_set_version: Literal["RRR-v0.1"]
    created_at: datetime
    members: list[_BaselineMemberFixture]


def baseline_reuse_permitted(inputs: BaselineReuseInputs) -> bool:
    return all(
        (
            inputs.authoritative_current_state_unchanged,
            inputs.baseline_scope_still_sufficient,
            inputs.configuration_context_still_valid,
            inputs.effectivity_context_still_valid,
            inputs.extraction_basis_still_accepted,
        )
    )


def reuse_assessment_baseline(
    session: Session,
    assessment_baseline_id: str,
    change_case_id: str,
    inputs: BaselineReuseInputs,
) -> AssessmentBaseline:
    if not baseline_reuse_permitted(inputs):
        raise ValueError("baseline reuse is not permitted by the five frozen validity inputs")
    baseline = session.get(AssessmentBaseline, assessment_baseline_id)
    if baseline is None:
        raise ValueError(f"Assessment Baseline {assessment_baseline_id} does not exist")
    if baseline.change_case_id != change_case_id:
        raise ValueError("Assessment Baseline belongs to another Change Case")
    return baseline


def read_canonical_baseline_snapshots(
    fixture_path: str | Path = DEFAULT_BASELINE_SNAPSHOT_FIXTURE,
) -> dict[str, _CanonicalSnapshotDefinition]:
    with Path(fixture_path).open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    return {
        alias: _CanonicalSnapshotDefinition.model_validate(value)
        for alias, value in raw.items()
    }


def read_frozen_baseline_fixture(
    scenario: str, fixture_path: str | Path | None = None
) -> _BaselineFixture:
    key = scenario.upper()
    if key not in DEFAULT_BASELINE_FIXTURES:
        raise ValueError("scenario must be A, B, or C")
    path = Path(fixture_path) if fixture_path is not None else DEFAULT_BASELINE_FIXTURES[key]
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    return _BaselineFixture.model_validate(raw)


def _utc_token(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    value = value.astimezone(timezone.utc)
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def _canonicalize_snapshot(
    object_type: BaselineObjectType, payload: dict[str, Any]
) -> dict[str, Any]:
    if object_type == "Product Version":
        return BaselineProductVersionSnapshot.model_validate(payload).model_dump(
            mode="json", exclude_none=True
        )
    if object_type == "Product Structure Occurrence":
        return BaselineOccurrenceSnapshot.model_validate(payload).model_dump(mode="json")
    if object_type == "Configuration Context":
        return BaselineConfigurationContextSnapshot.model_validate(payload).model_dump(
            mode="json"
        )
    if object_type == "Applicability Rule":
        return BaselineApplicabilityRuleSnapshot.model_validate(payload).model_dump(
            mode="json", by_alias=True
        )
    if object_type == "Effectivity Specification":
        return EffectivityPayload.model_validate(payload).model_dump(mode="json")
    if object_type == "Requirement":
        return BaselineRequirementSnapshot.model_validate(payload).model_dump(mode="json")
    raise ValueError(f"unsupported frozen baseline object type: {object_type}")


def _validate_snapshot_against_source(
    session: Session, member: BaselineMemberInput
) -> None:
    payload = member.snapshot_payload
    if member.object_type == "Product Version":
        source = session.get(ProductVersion, member.object_id)
        if source is None:
            raise ValueError(f"baseline Product Version {member.object_id} does not exist")
        expected = {
            "product_version_id": source.product_version_id,
            "product_element_id": source.product_element_id,
            "revision": source.revision,
            "iteration": source.iteration,
            "lifecycle_state": source.lifecycle_state,
        }
        if any(payload.get(key) != value for key, value in expected.items()):
            raise ValueError(
                f"Product Version snapshot for {member.object_id} mismatches source state"
            )
        return

    if member.object_type == "Product Structure Occurrence":
        source = session.get(ProductStructureOccurrence, member.object_id)
        if source is None:
            raise ValueError(f"baseline occurrence {member.object_id} does not exist")
        expected = {
            "occurrence_id": source.occurrence_id,
            "parent_product_version_id": source.parent_product_version_id,
            "child_product_version_id": source.child_product_version_id,
            "position": source.position,
            "quantity": source.quantity,
            "unit": source.unit,
            "applicability_rule": source.applicability_rule,
            "effectivity_specification": source.effectivity_specification,
        }
        if payload != expected:
            raise ValueError(
                f"Occurrence snapshot for {member.object_id} mismatches source state"
            )
        return

    if member.object_type == "Configuration Context":
        source = session.get(ConfigurationContext, member.object_id)
        if source is None:
            raise ValueError(f"Configuration Context {member.object_id} does not exist")
        expected = {
            "configuration_context_id": source.configuration_context_id,
            "name": source.name,
            "feature_values": source.feature_values,
            "completeness_state": source.completeness_state,
        }
        if payload != expected:
            raise ValueError(
                f"Configuration Context snapshot for {member.object_id} mismatches source state"
            )
        return

    if member.object_type == "Applicability Rule":
        rules = list(session.scalars(select(ProductStructureOccurrence)))
        if not any(
            occurrence.applicability_rule.get("rule_id") == member.object_id
            and payload["rule_id"] == occurrence.applicability_rule.get("rule_id")
            and payload["expression"] == occurrence.applicability_rule.get("expression")
            and payload["rule_version"] == occurrence.applicability_rule.get("rule_version")
            for occurrence in rules
        ):
            raise ValueError(
                f"Applicability Rule snapshot for {member.object_id} mismatches source state"
            )
        return

    if member.object_type == "Effectivity Specification":
        occurrences = list(session.scalars(select(ProductStructureOccurrence)))
        if payload not in [item.effectivity_specification for item in occurrences]:
            raise ValueError(
                f"Effectivity snapshot for {member.object_id} mismatches source state"
            )
        return

    if member.object_type == "Requirement":
        source = session.get(Requirement, member.object_id)
        if source is None:
            raise ValueError(f"Requirement {member.object_id} does not exist")
        expected = {
            "requirement_id": source.requirement_id,
            "requirement_revision": source.requirement_revision,
            "text": source.text,
            "allocated_product_element_id": source.allocated_product_element_id,
            "source_class": source.source_class,
            "source_identifier": source.source_identifier,
            "extraction_timestamp": _utc_token(source.extraction_timestamp),
        }
        if payload != expected:
            raise ValueError(
                f"Requirement snapshot for {member.object_id} mismatches source state"
            )
        return

    raise ValueError(f"unsupported frozen baseline object type: {member.object_type}")


def create_assessment_baseline(
    session: Session,
    baseline: AssessmentBaselineInput,
    members: list[BaselineMemberInput],
) -> AssessmentBaseline:
    if not members:
        raise ValueError("Assessment Baseline must contain at least one Baseline Member")
    if session.get(AssessmentBaseline, baseline.assessment_baseline_id) is not None:
        raise ValueError("Assessment Baseline already exists")
    if session.get(ConfigurationContext, baseline.configuration_context_id) is None:
        raise ValueError("Assessment Baseline Configuration Context does not exist")
    effectivity_payload = baseline.effectivity_context.model_dump(mode="json")
    source_effectivities = [
        occurrence.effectivity_specification
        for occurrence in session.scalars(select(ProductStructureOccurrence))
    ]
    if effectivity_payload not in source_effectivities:
        raise ValueError(
            "Assessment Baseline effectivity context does not match source state"
        )
    canonical_definitions = read_canonical_baseline_snapshots()
    canonical_by_identity = {
        (definition.object_type, definition.object_id): _canonicalize_snapshot(
            definition.object_type, definition.snapshot_payload
        )
        for definition in canonical_definitions.values()
    }
    for member in members:
        if member.assessment_baseline_id != baseline.assessment_baseline_id:
            raise ValueError("Baseline Member references another Assessment Baseline")
        canonical = _canonicalize_snapshot(member.object_type, member.snapshot_payload)
        expected_canonical = canonical_by_identity.get(
            (member.object_type, member.object_id)
        )
        if expected_canonical is None or canonical != expected_canonical:
            raise ValueError(
                f"Baseline Member {member.baseline_member_id} does not match the frozen canonical snapshot"
            )
        _validate_snapshot_against_source(session, member)

    record = AssessmentBaseline(
        **baseline.model_dump(mode="python", exclude={"effectivity_context"}),
        effectivity_context=baseline.effectivity_context.model_dump(mode="json"),
    )
    session.add(record)
    session.flush()
    session.add_all([BaselineMember(**member.model_dump()) for member in members])
    session.flush()
    return record


def frozen_baseline_inputs(
    scenario: str,
) -> tuple[AssessmentBaselineInput, list[BaselineMemberInput]]:
    fixture = read_frozen_baseline_fixture(scenario)
    snapshots = read_canonical_baseline_snapshots()
    baseline = AssessmentBaselineInput(
        assessment_baseline_id=fixture.assessment_baseline_id,
        change_case_id=fixture.change_case_id,
        snapshot_timestamp=fixture.snapshot_timestamp,
        configuration_context_id=fixture.configuration_context_id,
        effectivity_context=fixture.effectivity_context,
        rule_set_version=fixture.rule_set_version,
        created_at=fixture.created_at,
    )
    members: list[BaselineMemberInput] = []
    for item in fixture.members:
        definition = snapshots.get(item.snapshot_alias)
        if definition is None:
            raise ValueError(f"unknown canonical snapshot alias {item.snapshot_alias}")
        if (
            definition.object_type != item.object_type
            or definition.object_id != item.object_id
        ):
            raise ValueError(
                f"snapshot alias {item.snapshot_alias} does not match member identity"
            )
        members.append(
            BaselineMemberInput(
                baseline_member_id=item.baseline_member_id,
                assessment_baseline_id=fixture.assessment_baseline_id,
                object_type=item.object_type,
                object_id=item.object_id,
                object_revision_or_state_token=item.object_revision_or_state_token,
                source_identifier=item.source_identifier,
                snapshot_payload=_canonicalize_snapshot(
                    definition.object_type, definition.snapshot_payload
                ),
            )
        )
    return baseline, members


def load_frozen_baseline_fixture(session: Session, scenario: str) -> AssessmentBaseline:
    baseline, members = frozen_baseline_inputs(scenario)
    return create_assessment_baseline(session, baseline, members)
