from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from plm_ref.application.baseline import BaselineReuseInputs, reuse_assessment_baseline
from plm_ref.application.change_case import ChangeItemRevisionInput, ProposalStateInput, create_change_item
from plm_ref.application.gate_a import evaluate_gate_a
from plm_ref.application.overlay import OverlayRevisionInput, create_overlay_revision
from plm_ref.application.scope_routing import ScopeRouteCommand, evaluate_scope_route
from plm_ref.application.source_projection import load_shared_source_fixture
from plm_ref.infrastructure.db.models import Assessment, AssessmentBaseline, AssessmentImpactLink, AssessmentRequirementConclusion, ChangeItem, ChangeItemProposalState, ChangeItemRevision, OverlayChangeItemMembership, OverlayLocalObject, ProcessHistoryEntry
from plm_ref.infrastructure.db.session import create_sqlite_engine
from plm_ref.rules.rrr_v01 import Rrr05Input, evaluate_rrr05
from test_g07_assessment import _complete_scenario, _dt, _prepare


@pytest.fixture
def engine(tmp_path: Path):
    path = tmp_path / "g08.db"
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


def _command() -> ScopeRouteCommand:
    return ScopeRouteCommand("IAX-B01", "HIST-B01", _dt("2026-08-25T21:00:00Z"),
        "Change Owner B", "Domain Assessment", "Scope Confirmation",
        "ASM-B01 concluded that PSO-002 applicability must change explicitly; discovered impact is not authorised scope.")


def _b02_revision() -> ChangeItemRevisionInput:
    return ChangeItemRevisionInput(
        change_item_id="CI-B02", change_item_revision="r1", change_case_id="CHG-B01",
        action="Change Applicability", target_type="Product Structure Occurrence", target_id="PSO-002",
        current_state_reference={"occurrence_id": "PSO-002", "applicability_rule_id": "APP-001", "applicability_rule_version": "1"},
        proposed_state_payload={"applicability_rule": {"rule_id": "APP-B02",
            "expression": 'CoolingType = "Liquid" AND PackFamily = "LongRange"', "rule_version": "1"}},
        reason="Align occurrence applicability with the validated scope of the proposed Cooling Plate state.",
        owner="Change Owner B", configuration_context_id="CFG-001",
        intended_effectivity={"effectivity_type": "Planned Engineering Effective Date", "planned_effective_date": "2026-11-01"},
        revision_created_at=_dt("2026-08-25T21:05:00Z"))


def _b02_proposal() -> ProposalStateInput:
    return ProposalStateInput(change_item_id="CI-B02", change_case_id="CHG-B01", selected_revision="r1",
        proposal_state="Active", state_changed_at=_dt("2026-08-25T21:06:00Z"), state_changed_by="Change Owner B")


def test_it10_b_scope_route_then_explicit_amendment_and_overlay(engine) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, "B")
        entry = evaluate_scope_route(session, _command())
        assert entry is not None
        assert (entry.process_history_id, entry.change_case_id, entry.entry_type, entry.timestamp,
                entry.actor, entry.origin_stage, entry.target_stage_or_route, entry.reason,
                entry.affected_change_item_id, entry.affected_change_item_revision) == (
                "HIST-B01", "CHG-B01", "Scope Revision Required", _dt("2026-08-25T21:00:00Z"),
                "Change Owner B", "Domain Assessment", "Scope Confirmation",
                "ASM-B01 concluded that PSO-002 applicability must change explicitly; discovered impact is not authorised scope.",
                "CI-B01", "r1")
        assert session.get(ChangeItem, "CI-B02") is None
        create_change_item(session, _b02_revision(), _b02_proposal())
        revision = session.get(ChangeItemRevision, ("CI-B02", "r1"))
        assert revision is not None
        assert (revision.change_case_id, revision.action, revision.target_type, revision.target_id,
                revision.current_state_reference, revision.proposed_state_payload, revision.reason,
                revision.owner, revision.configuration_context_id, revision.intended_effectivity,
                revision.revision_created_at) == (
                "CHG-B01", "Change Applicability", "Product Structure Occurrence", "PSO-002",
                {"occurrence_id": "PSO-002", "applicability_rule_id": "APP-001", "applicability_rule_version": "1"},
                {"applicability_rule": {"rule_id": "APP-B02", "expression": 'CoolingType = "Liquid" AND PackFamily = "LongRange"', "rule_version": "1"}},
                "Align occurrence applicability with the validated scope of the proposed Cooling Plate state.",
                "Change Owner B", "CFG-001",
                {"effectivity_type": "Planned Engineering Effective Date", "planned_effective_date": "2026-11-01"},
                _dt("2026-08-25T21:05:00Z").replace(tzinfo=None))
        b01_proposal = session.get(ChangeItemProposalState, "CI-B01")
        b02_proposal = session.get(ChangeItemProposalState, "CI-B02")
        assert (b01_proposal.proposal_state, b02_proposal.change_case_id, b02_proposal.selected_revision,
                b02_proposal.proposal_state, b02_proposal.state_changed_at, b02_proposal.state_changed_by) == (
                "Active", "CHG-B01", "r1", "Active", _dt("2026-08-25T21:06:00Z").replace(tzinfo=None), "Change Owner B")
        gate = evaluate_gate_a(session, "CHG-B01")
        assert gate.passed and gate.active_change_items == ("CI-B01:r1", "CI-B02:r1")
        inputs = BaselineReuseInputs(authoritative_current_state_unchanged=True,
            baseline_scope_still_sufficient=True, configuration_context_still_valid=True,
            effectivity_context_still_valid=True, extraction_basis_still_accepted=True)
        assert reuse_assessment_baseline(session, "BL-B01", "CHG-B01", inputs).assessment_baseline_id == "BL-B01"
        create_overlay_revision(session, "BL-B01", OverlayRevisionInput(
            overlay_revision_id="OV-B02", change_case_id="CHG-B01", created_at=_dt("2026-08-25T21:10:00Z")),
            local_object_ids={"CI-B01": "OVOBJ-B02-PV", "CI-B02": "OVOBJ-B02-PSO"})
        assert list(session.execute(select(OverlayChangeItemMembership.change_item_id,
            OverlayChangeItemMembership.change_item_revision).where(
            OverlayChangeItemMembership.overlay_revision_id == "OV-B02").order_by(
            OverlayChangeItemMembership.change_item_id))) == [("CI-B01", "r1"), ("CI-B02", "r1")]
        objects = {o.overlay_local_object_id: o for o in session.scalars(select(OverlayLocalObject).where(OverlayLocalObject.overlay_revision_id == "OV-B02"))}
        assert set(objects) == {"OVOBJ-B02-PV", "OVOBJ-B02-PSO"}
        assert objects["OVOBJ-B02-PSO"].state_payload["child_product_version_reference"] == "OVOBJ-B02-PV"
        assert objects["OVOBJ-B02-PSO"].state_payload["applicability_rule"] == {"rule_id": "APP-B02", "expression": 'CoolingType = "Liquid" AND PackFamily = "LongRange"', "rule_version": "1"}
        assert len(list(session.scalars(select(AssessmentBaseline).where(AssessmentBaseline.change_case_id == "CHG-B01")))) == 1


@pytest.mark.parametrize("overrides", [
    {"req_004_conclusion": "Satisfied"},
    {"product_engineering_assessment_complete": False},
    {"assessment_linked_to_occurrence_candidate": False},
    {"validated_scope_relation": "Equal"},
    {"overlay_contains_matching_applicability_change": True},
])
def test_rrr05_negative_structured_conditions(overrides) -> None:
    values = dict(validated_scope_relation="Proposed Narrower",
        product_engineering_assessment_complete=True,
        assessment_linked_to_occurrence_candidate=True,
        req_004_conclusion="Not Satisfied",
        overlay_contains_matching_applicability_change=False)
    values.update(overrides)
    assert evaluate_rrr05(Rrr05Input(**values), frozenset({("CI-B01", "r1")})) is None


def test_rrr05_is_narrative_independent_and_ambiguous_provenance_is_null() -> None:
    inputs = Rrr05Input("Proposed Narrower", True, True, "Not Satisfied", False)
    assert evaluate_rrr05(inputs, frozenset({("CI-B01", "r1")})).affected_change_item_id == "CI-B01"
    ambiguous = evaluate_rrr05(inputs, frozenset({("CI-B01", "r1"), ("CI-X", "r2")}))
    assert ambiguous is not None
    assert (ambiguous.affected_change_item_id, ambiguous.affected_change_item_revision) == (None, None)


@pytest.mark.parametrize(("domain", "state"), [("Product Engineering", "Submitted"), ("Validation", "Complete")])
def test_scope_route_does_not_fire_for_wrong_domain_or_incomplete_assessment(engine, domain: str, state: str) -> None:
    with Session(engine) as session, session.begin():
        _prepare(session, "B")
        session.add(Assessment(assessment_id="ASM-NEG", change_case_id="CHG-B01",
            origin_impact_execution_id="IAX-B01", domain=domain, assessment_state=state,
            relevance="Relevant", disposition="No Objection", impact_statement="ignored narrative",
            assessor="tester", completed_at=None, is_locked=False))
        session.flush()
        session.add(AssessmentImpactLink(assessment_id="ASM-NEG", impact_candidate_id="IC-B01"))
        session.add(AssessmentRequirementConclusion(assessment_requirement_conclusion_id="ARC-NEG",
            assessment_id="ASM-NEG", requirement_id="REQ-004", conclusion="Not Satisfied"))
        assert evaluate_scope_route(session, _command()) is None
        assert session.get(ProcessHistoryEntry, "HIST-B01") is None
        assert session.get(ChangeItem, "CI-B02") is None


def test_process_history_migration_contains_no_decision_boundary(engine) -> None:
    tables = set(inspect(engine).get_table_names())
    assert "process_history_entries" in tables
    assert not {"decision_records", "decision_support_assessments", "decision_scope_items", "decision_conditions"} & tables
