from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from plm_ref.application.assessment import EvidenceUseInput, complete_assessment
from plm_ref.application.assessment_reuse import (
    RetainedFulfilment, classify_assessment_reuse, fulfil_from_retained_assessments,
)
from plm_ref.application.authority import (
    EscalationCommand, evaluate_authority, persist_escalation,
)
from plm_ref.application.change_case import (
    ChangeCaseInput, ChangeItemRevisionInput, OpenItemInput, ProposalStateInput,
    create_change_case, create_change_item, create_open_item,
)
from plm_ref.application.readiness import (
    _mandatory_candidates_covered, derive_case_state, evaluate_authorisation_eligibility,
    evaluate_gate_b,
)
from plm_ref.application.scope_routing import evaluate_scope_route
from plm_ref.application.source_projection import load_shared_source_fixture
from plm_ref.domain.errors import AssessmentCompletionError
from plm_ref.infrastructure.db.models import (
    AssessmentObligation, ChangeCase, ImpactExecution, OpenItem, ProcessHistoryEntry,
)
from plm_ref.infrastructure.db.session import create_sqlite_engine
from test_g07_assessment import _complete_scenario, _dt, _input, _prepare
from test_g08_scope_route import _command
from test_g09_assessment_reuse import _prepare_second_cycle


@pytest.fixture
def engine(tmp_path: Path):
    path = tmp_path / "g10.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{path}")
    command.upgrade(config, "head")
    db = create_sqlite_engine(path)
    with Session(db) as session, session.begin():
        load_shared_source_fixture(session)
    try:
        yield db
    finally:
        db.dispose()


def _complete_c_with(session: Session, *, index: int, disposition: str = "No Objection",
                     conclusion: str = "Satisfied") -> None:
    _prepare(session, "C")
    for current in range(1, 5):
        data = _input("C", current)
        if current == index:
            data = data.__class__(
                **{**data.__dict__, "disposition": disposition,
                   "requirement_conclusions": (() if current == 4 else (
                       data.requirement_conclusions[0].__class__(
                           data.requirement_conclusions[0].assessment_requirement_conclusion_id,
                           data.requirement_conclusions[0].requirement_id, conclusion),))}
            )
        complete_assessment(session, data)


def test_scenario_a_gate_b_authority_and_no_terminal_decision(engine) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, "A")
        gate = evaluate_gate_b(session, "IAX-A01")
        eligibility = evaluate_authorisation_eligibility(session, gate)
        authority = evaluate_authority(gate, eligibility)
        assert (gate.gate_b, gate.required_authority_level, gate.rrr_06_evaluated) == (
            "Complete", "Standard", True)
        assert eligibility.authorisation_eligibility == "Permitted"
        assert (authority.current_authority_level, authority.authority_sufficient,
                authority.decision_permitted, authority.escalation_required) == (
            "Standard", True, True, False)
        assert derive_case_state(session, gate).case_state == "Decision Ready"
        assert not inspect(session.bind).has_table("decision_records")


def test_scenario_b_stops_before_rrr06_and_remains_in_assessment(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_second_cycle(session)
        classify_assessment_reuse(session, "IAX-B02")
        fulfil_from_retained_assessments(session, (
            RetainedFulfilment("AO-B23", "ASM-B02"), RetainedFulfilment("AO-B24", "ASM-B04")))
        gate = evaluate_gate_b(session, "IAX-B02")
        eligibility = evaluate_authorisation_eligibility(session, gate)
        authority = evaluate_authority(gate, eligibility)
        obligations = list(session.scalars(select(AssessmentObligation).where(
            AssessmentObligation.impact_execution_id == "IAX-B02").order_by(
            AssessmentObligation.assessment_obligation_id)))
        assert [o.fulfilled_by_assessment_id for o in obligations] == [None, None, "ASM-B02", "ASM-B04"]
        assert (gate.gate_b, gate.required_authority_level, gate.rrr_06_evaluated,
                gate.failed_predicate) == ("Incomplete", "Not Evaluated", False,
                    "all_mandatory_obligations_satisfied")
        assert eligibility.authorisation_eligibility == "Not Evaluated"
        assert (authority.current_authority_level, authority.decision_permitted,
                authority.escalation_required) == ("Not Evaluated", None, None)
        assert not _mandatory_candidates_covered(session, session.get(ImpactExecution, "IAX-B02"), obligations)
        assert derive_case_state(session, gate).case_state == "In Assessment"


def test_it12_scenario_c_escalates_non_terminal_and_is_idempotent(engine) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, "C")
        gate = evaluate_gate_b(session, "IAX-C01")
        eligibility = evaluate_authorisation_eligibility(session, gate)
        authority = evaluate_authority(gate, eligibility)
        assert (gate.gate_b, gate.required_authority_level) == ("Complete", "Elevated")
        assert eligibility.authorisation_eligibility == "Permitted"
        assert (authority.current_authority_level, authority.authority_sufficient,
                authority.decision_permitted, authority.escalation_required) == (
            "Standard", False, False, True)
        entry = persist_escalation(session, authority, EscalationCommand(
            "HIST-C01", _dt("2026-08-25T22:20:00Z"), "Decision Coordinator C"))
        assert (entry.process_history_id, entry.change_case_id, entry.entry_type, entry.timestamp,
                entry.actor, entry.origin_stage, entry.target_stage_or_route, entry.reason,
                entry.affected_change_item_id, entry.affected_change_item_revision) == (
            "HIST-C01", "CHG-C01", "Escalated", _dt("2026-08-25T22:20:00Z"),
            "Decision Coordinator C", "Authority Check", "Elevated Authority Route",
            "Required authority is Elevated while current authority is Standard.", "CI-C01", "r1")
        assert session.get(ChangeCase, "CHG-C01").case_state == "Decision Ready"
        with pytest.raises(ValueError):
            persist_escalation(session, authority, EscalationCommand(
                "HIST-C01", _dt("2026-08-25T22:20:00Z"), "Decision Coordinator C"))
        assert session.scalar(select(ProcessHistoryEntry.process_history_id).where(
            ProcessHistoryEntry.process_history_id == "HIST-C01")) == "HIST-C01"
        assert not inspect(session.bind).has_table("decision_records")


@pytest.mark.parametrize(("disposition", "conclusion"), [
    ("No Objection", "Not Satisfied"), ("No Objection", "Not Demonstrated"),
    ("Objection", "Satisfied"), ("Escalation Recommended", "Satisfied"),
    ("No Objection with Conditions", "Satisfied"),
])
def test_it11_gate_b_is_separate_from_substantive_eligibility(
    engine, disposition: str, conclusion: str,
) -> None:
    with Session(engine) as session, session.begin():
        _complete_c_with(session, index=1, disposition=disposition, conclusion=conclusion)
        gate = evaluate_gate_b(session, "IAX-C01")
        eligibility = evaluate_authorisation_eligibility(session, gate)
        assert gate.gate_b == "Complete"
        expected = "Permitted" if disposition == "No Objection with Conditions" else "Blocked"
        assert eligibility.authorisation_eligibility == expected


@pytest.mark.parametrize(("field", "value", "predicate"), [
    ("execution_status", "Running", "impact_execution_completed"),
    ("routing_status", "Not Started", "assessment_routing_completed"),
])
def test_gate_b_pre_authority_lifecycle_short_circuit(engine, field: str, value: str, predicate: str) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, "A")
        setattr(session.get(ImpactExecution, "IAX-A01"), field, value)
        gate = evaluate_gate_b(session, "IAX-A01")
        assert (gate.gate_b, gate.failed_predicate, gate.rrr_06_evaluated,
                gate.required_authority_level) == ("Incomplete", predicate, False, "Not Evaluated")


def test_gate_b_rejects_outstanding_scope_route(engine) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, "B")
        assert evaluate_scope_route(session, _command()) is not None
        gate = evaluate_gate_b(session, "IAX-B01")
        assert (gate.gate_b, gate.failed_predicate, gate.rrr_06_evaluated) == (
            "Incomplete", "scope_revision_route_outstanding", False)


def test_gate_b_rejects_overlay_scope_mismatch(engine) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, "A")
        create_change_item(session, ChangeItemRevisionInput(
            change_item_id="CI-A02", change_item_revision="r1", change_case_id="CHG-A01",
            action="Change Applicability", target_type="Product Structure Occurrence", target_id="PSO-002",
            current_state_reference={"occurrence_id": "PSO-002", "applicability_rule_id": "APP-001", "applicability_rule_version": "1"},
            proposed_state_payload={"applicability_rule": {"rule_id": "APP-A02", "expression": 'CoolingType = "Liquid"', "rule_version": "1"}},
            reason="fixture", owner="Change Owner A", configuration_context_id="CFG-001",
            intended_effectivity={"effectivity_type": "Planned Engineering Effective Date", "planned_effective_date": "2026-11-01"},
            revision_created_at=_dt("2026-08-25T19:50:00Z")),
            ProposalStateInput(change_item_id="CI-A02", change_case_id="CHG-A01", selected_revision="r1",
                proposal_state="Active", state_changed_at=_dt("2026-08-25T19:51:00Z"), state_changed_by="Change Owner A"))
        gate = evaluate_gate_b(session, "IAX-A01")
        assert (gate.gate_b, gate.failed_predicate, gate.rrr_06_evaluated) == (
            "Incomplete", "exact_proposed_change_scope_known", False)


def test_gate_b_rejects_unresolved_decision_open_item(engine) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, "A")
        session.add(OpenItem(open_item_id="OI-A10", change_case_id="CHG-A01", source_type="Fixture",
            source_id="IAX-A01", item_type="Required Action", description="fixture", owner="fixture",
            status="Open", blocking_class="Blocking", required_before_stage="Decision",
            resolution_evidence_reference=None, created_at=_dt("2026-08-25T19:50:00Z"), closed_at=None))
        gate = evaluate_gate_b(session, "IAX-A01")
        assert (gate.gate_b, gate.failed_predicate) == ("Incomplete", "decision_blocking_open_items_resolved")


@pytest.mark.parametrize("evidence", [
    (),
    (EvidenceUseInput("AEU-A01-NEG", "EV-003", "OVOBJ-A01-PV",
        "Not Applicable to Proposed State", "EV-003@2026-08-25T18:10:00Z"),),
])
def test_missing_or_incompatible_evidence_leaves_gate_b_incomplete(engine, evidence) -> None:
    with Session(engine) as session, session.begin():
        _prepare(session, "A")
        with pytest.raises(AssessmentCompletionError):
            complete_assessment(session, _input("A", 1, evidence=evidence))
        for index in range(2, 5):
            complete_assessment(session, _input("A", index))
        gate = evaluate_gate_b(session, "IAX-A01")
        assert (gate.gate_b, gate.required_authority_level, gate.rrr_06_evaluated) == (
            "Incomplete", "Not Evaluated", False)


@pytest.mark.parametrize("trigger", ["Unknown frozen trigger", "Synthetic supplier process change "])
def test_unmapped_or_near_match_authority_trigger_fails_closed(engine, trigger: str) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, "A")
        session.get(ChangeCase, "CHG-A01").trigger = trigger
        gate = evaluate_gate_b(session, "IAX-A01")
        assert (gate.gate_b, gate.failed_predicate, gate.rrr_06_evaluated,
                gate.required_authority_level) == ("Incomplete", "required_authority_level_is_known", True, "Not Evaluated")


def test_cross_case_open_item_cannot_influence_readiness(engine) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, "A")
        create_change_case(session, ChangeCaseInput(
            change_case_id="CHG-X", title="x", trigger="Unknown frozen trigger", rationale="x", change_owner="x",
            case_state="Open", process_iteration=1, created_at=_dt("2026-08-25T19:50:00Z"), closed_at=None))
        create_open_item(session, OpenItemInput(
            open_item_id="OI-X", change_case_id="CHG-X", source_type="Fixture", source_id="x",
            item_type="Required Action", description="x", owner="x", status="Open", blocking_class="Blocking",
            required_before_stage="Decision", created_at=_dt("2026-08-25T19:50:00Z")))
        gate = evaluate_gate_b(session, "IAX-A01")
        assert (gate.gate_b, gate.required_authority_level) == ("Complete", "Standard")
