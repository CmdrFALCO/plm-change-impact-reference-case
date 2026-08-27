"""INC-14 independent expected-oracle comparison and deterministic evidence helpers."""
from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from pathlib import Path
from collections.abc import Mapping
from typing import Any

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from plm_ref.application.authority import evaluate_authority
from plm_ref.application.history_and_views import derive_case_handover_view, reconstruct_decision_basis
from plm_ref.application.readiness import evaluate_authorisation_eligibility, evaluate_gate_b
from plm_ref.infrastructure.db.base import Base
from plm_ref.infrastructure.db.models import (
    Assessment, AssessmentEvidenceUse, AssessmentImpactLink, AssessmentObligation,
    AssessmentRequirementConclusion, AssessmentReuseClassification, AssessmentBaseline,
    BaselineMember, ChangeCase, ChangeItem, ChangeItemProposalState, ChangeItemRevision,
    DecisionCondition, DecisionRecord, DecisionScopeItem, DecisionSupportAssessment,
    ImpactCandidate, ImpactCandidatePathStep, ImpactCandidateProvenance, ImpactExecution,
    OverlayChangeItemMembership, OverlayLocalObject, OverlayRevision, ProcessHistoryEntry,
)

ROOT = Path(__file__).resolve().parents[3]


def _json(value: Any) -> Any:
    if is_dataclass(value):
        return {field.name: _json(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _json(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_json(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat().replace("+00:00", "Z")
    return value


def canonical_actual(session: Session, scenario: str) -> dict[str, Any]:
    """Capture all domain tables and required derived state in deterministic order."""
    scenario = scenario.upper()
    case_id = f"CHG-{scenario}01"
    execution_ids = sorted(row.impact_execution_id for row in session.scalars(select(ImpactExecution).where(ImpactExecution.change_case_id == case_id)))
    baselines = {row.assessment_baseline_id for row in session.scalars(select(AssessmentBaseline).where(AssessmentBaseline.change_case_id == case_id))}
    overlays = {row.overlay_revision_id for row in session.scalars(select(OverlayRevision).where(OverlayRevision.change_case_id == case_id))}
    candidates = {row.impact_candidate_id for row in session.scalars(select(ImpactCandidate).where(ImpactCandidate.impact_execution_id.in_(execution_ids)))}
    provenances = {row.impact_candidate_provenance_id for row in session.scalars(select(ImpactCandidateProvenance).where(ImpactCandidateProvenance.impact_candidate_id.in_(candidates)))}
    assessments = {row.assessment_id for row in session.scalars(select(Assessment).where(Assessment.change_case_id == case_id))}
    decisions = {row.decision_record_id for row in session.scalars(select(DecisionRecord).where(DecisionRecord.change_case_id == case_id))}
    filters = {
        ChangeCase: ChangeCase.change_case_id == case_id, ChangeItem: ChangeItem.change_case_id == case_id,
        ChangeItemRevision: ChangeItemRevision.change_case_id == case_id, ChangeItemProposalState: ChangeItemProposalState.change_case_id == case_id,
        AssessmentBaseline: AssessmentBaseline.change_case_id == case_id, BaselineMember: BaselineMember.assessment_baseline_id.in_(baselines),
        OverlayRevision: OverlayRevision.change_case_id == case_id, OverlayChangeItemMembership: OverlayChangeItemMembership.overlay_revision_id.in_(overlays),
        OverlayLocalObject: OverlayLocalObject.overlay_revision_id.in_(overlays), ImpactExecution: ImpactExecution.impact_execution_id.in_(execution_ids),
        ImpactCandidate: ImpactCandidate.impact_candidate_id.in_(candidates), ImpactCandidateProvenance: ImpactCandidateProvenance.impact_candidate_provenance_id.in_(provenances),
        ImpactCandidatePathStep: ImpactCandidatePathStep.impact_candidate_provenance_id.in_(provenances), AssessmentObligation: AssessmentObligation.impact_execution_id.in_(execution_ids),
        Assessment: Assessment.assessment_id.in_(assessments), AssessmentImpactLink: AssessmentImpactLink.assessment_id.in_(assessments),
        AssessmentRequirementConclusion: AssessmentRequirementConclusion.assessment_id.in_(assessments), AssessmentEvidenceUse: AssessmentEvidenceUse.assessment_id.in_(assessments),
        AssessmentReuseClassification: AssessmentReuseClassification.target_impact_execution_id.in_(execution_ids), ProcessHistoryEntry: ProcessHistoryEntry.change_case_id == case_id,
        DecisionRecord: DecisionRecord.decision_record_id.in_(decisions), DecisionScopeItem: DecisionScopeItem.decision_record_id.in_(decisions),
        DecisionSupportAssessment: DecisionSupportAssessment.decision_record_id.in_(decisions), DecisionCondition: DecisionCondition.decision_record_id.in_(decisions),
    }
    tables: dict[str, list[dict[str, Any]]] = {}
    for model, criterion in filters.items():
        rows = [{column.name: _json(getattr(row, column.name)) for column in row.__table__.columns} for row in session.scalars(select(model).where(criterion))]
        tables[model.__tablename__] = sorted(rows, key=lambda row: json.dumps(row, sort_keys=True, separators=(",", ":")))
    derived: dict[str, Any] = {"executions": {}}
    for execution_id in execution_ids:
        gate = evaluate_gate_b(session, execution_id)
        eligibility = evaluate_authorisation_eligibility(session, gate)
        derived["executions"][execution_id] = _json({"gate_b": gate, "eligibility": eligibility, "authority": evaluate_authority(gate, eligibility)})
    decision = session.scalar(select(DecisionRecord).where(DecisionRecord.change_case_id == case_id))
    derived["handover"] = _json(derive_case_handover_view(session, case_id))
    if decision is not None:
        derived["historical_basis"] = _json(reconstruct_decision_basis(session, decision.decision_record_id))
    return {"scenario": scenario, "tables": tables, "derived": derived}


def load_expected(scenario: str, root: Path = ROOT) -> dict[str, Any]:
    path = root / "data" / "scenarios" / f"scenario_{scenario.lower()}" / "expected.yaml"
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _diff(expected: Any, actual: Any, path: str = "$") -> list[dict[str, Any]]:
    if type(expected) is not type(actual):
        return [{"path": path, "expected": expected, "actual": actual}]
    if isinstance(expected, dict):
        diffs = []
        for key in sorted(set(expected) | set(actual)):
            if key not in expected: diffs.append({"path": f"{path}.{key}", "expected": "<missing>", "actual": actual[key]})
            elif key not in actual: diffs.append({"path": f"{path}.{key}", "expected": expected[key], "actual": "<missing>"})
            else: diffs.extend(_diff(expected[key], actual[key], f"{path}.{key}"))
        return diffs
    if isinstance(expected, list):
        diffs = []
        if len(expected) != len(actual): diffs.append({"path": path + ".length", "expected": len(expected), "actual": len(actual)})
        for index, (left, right) in enumerate(zip(expected, actual)): diffs.extend(_diff(left, right, f"{path}[{index}]"))
        return diffs
    return [] if expected == actual else [{"path": path, "expected": expected, "actual": actual}]


def _project(actual: Any, expected: Any) -> Any:
    """Project actual to the frozen oracle shape; lists retain every actual row."""
    if isinstance(expected, dict) and isinstance(actual, dict):
        return {key: _project(actual[key], value) for key, value in expected.items() if key in actual}
    if isinstance(expected, list) and isinstance(actual, list):
        return [_project(item, expected[0]) for item in actual] if expected else actual
    return actual


def compare_scenario(session: Session, scenario: str, expected: dict[str, Any] | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    actual = canonical_actual(session, scenario)
    oracle = load_expected(scenario) if expected is None else expected
    return actual, _diff(oracle, _project(actual, oracle))
