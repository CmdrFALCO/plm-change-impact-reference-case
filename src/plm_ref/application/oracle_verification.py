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


def compare_scenario(session: Session, scenario: str, expected: dict[str, Any] | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    actual = canonical_actual(session, scenario)
    oracle = load_expected(scenario) if expected is None else expected
    return actual, _diff(oracle, actual)


def verify_historical_basis(actual: dict[str, Any], expected: dict[str, Any]) -> list[dict[str, Any]]:
    """Compare the independently frozen complete DEC-A01 historical basis."""
    return _diff(expected["derived"]["historical_basis"], actual["derived"].get("historical_basis"), "$.historical_basis")


def cross_scenario_results(actuals: Mapping[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Evaluate the frozen §9 cross-scenario assertions from canonical state."""
    a, b, c = actuals["A"], actuals["B"], actuals["C"]
    def rows(state: dict[str, Any], table: str) -> list[dict[str, Any]]: return state["tables"][table]
    results = {
        "A only terminal Decision": len(rows(a, "decision_records")) == 1 and not rows(b, "decision_records") and not rows(c, "decision_records"),
        "B only two proposal cycles": len(rows(b, "impact_executions")) == 2 and len(rows(a, "impact_executions")) == len(rows(c, "impact_executions")) == 1,
        "B baseline reuse": len(rows(b, "assessment_baselines")) == 1 and {row["assessment_baseline_id"] for row in rows(b, "impact_executions")} == {"BL-B01"},
        "historical overlays distinct": {row["overlay_revision_id"] for row in rows(b, "overlay_revisions")} == {"OV-B01", "OV-B02"},
        "retained Assessment semantics": {row["assessment_id"]: row["classification"] for row in rows(b, "assessment_reuse_classifications")} == {"ASM-B01": "Invalidated", "ASM-B02": "Retained", "ASM-B03": "Revalidation Required", "ASM-B04": "Retained"},
        "A Decision Scope exact": [(row["change_item_id"], row["change_item_revision"]) for row in rows(a, "decision_scope_items")] == [("CI-A01", "r1")],
        "A zero Decision Conditions": not rows(a, "decision_conditions"),
        "B and C no Handover": b["derived"]["handover"] is None and c["derived"]["handover"] is None,
        "C authority insufficiency non-terminal": c["derived"]["executions"]["IAX-C01"]["authority"]["escalation_required"] is True and not rows(c, "decision_records"),
    }
    for state in (a, b, c):
        case = f"CHG-{state['scenario']}01"
        results[f"{state['scenario']} case-local lineage"] = all(row.get("change_case_id", case) == case for table in state["tables"].values() for row in table)
    return {name: {"passed": passed} for name, passed in results.items()}


def integrity_results(actuals: Mapping[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Deterministic release-integrity catalogue, including all IT-16 families."""
    a, b, c = actuals["A"], actuals["B"], actuals["C"]
    def rows(state: dict[str, Any], table: str) -> list[dict[str, Any]]: return state["tables"][table]
    def execution_case_local(state: dict[str, Any]) -> bool:
        baselines = {row["assessment_baseline_id"]: row["change_case_id"] for row in rows(state, "assessment_baselines")}
        overlays = {row["overlay_revision_id"]: row["change_case_id"] for row in rows(state, "overlay_revisions")}
        return all(baselines.get(row["assessment_baseline_id"]) == row["change_case_id"] and overlays.get(row["overlay_revision_id"]) == row["change_case_id"] for row in rows(state, "impact_executions"))
    family = {
        "IT-16 execution baseline/overlay": all(execution_case_local(state) for state in (a, b, c)),
        "IT-16 candidate provenance": all(provenance["change_item_id"].split("-")[1][0] == state["scenario"] for state in (a,b,c) for provenance in rows(state,"impact_candidate_provenance")),
        "IT-16 Assessment fulfilment": all(obligation["fulfilled_by_assessment_id"] is None or obligation["fulfilled_by_assessment_id"].split("-")[1][0] == state["scenario"] for state in (a,b,c) for obligation in rows(state,"assessment_obligations")),
        "IT-16 Assessment reuse": all(row["assessment_id"].startswith("ASM-B") and row["target_impact_execution_id"] == "IAX-B02" for row in rows(b,"assessment_reuse_classifications")),
        "IT-16 Decision support": all(row["assessment_id"].startswith("ASM-A") and row["decision_record_id"] == "DEC-A01" for row in rows(a,"decision_support_assessments")),
        "IT-16 Decision Scope": all(row["change_item_id"] == "CI-A01" and row["change_item_revision"] == "r1" for row in rows(a,"decision_scope_items")),
    }
    return {name: {"passed": passed} for name, passed in family.items()}
