from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from plm_ref.application.baseline import read_canonical_baseline_snapshots
from plm_ref.application.decision import persist_terminal_decision
from plm_ref.application.history_and_views import (
    derive_case_handover_view, derive_handover_view, reconstruct_decision_basis,
)
from plm_ref.application.source_projection import load_shared_source_fixture
from plm_ref.infrastructure.db.models import DecisionRecord, EvidenceRecord
from plm_ref.infrastructure.db.session import create_sqlite_engine
from test_g07_assessment import _complete_scenario
from test_g11_terminal_decision import _command


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)


@pytest.fixture
def engine(tmp_path: Path):
    path = tmp_path / "g12.db"
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


def _decision(session: Session) -> None:
    _complete_scenario(session, "A")
    persist_terminal_decision(session, _command())


def _by_id(records):
    return {record.record_id: record.fields for record in records}


def _evidence_snapshot(evidence_id, evidence_type, reference, requirement_id, result, issue_date, provider, source_identifier):
    return {"evidence_record_id": evidence_id, "evidence_type": evidence_type, "reference": reference,
        "applicable_product_version_id": "PV-003", "configuration_context_id": "CFG-001", "requirement_id": requirement_id,
        "result": result, "issue_date": issue_date, "validity_state": "Current", "provider": provider,
        "superseded_by_evidence_id": None, "source_class": "Evidence Source", "source_identifier": source_identifier,
        "extraction_timestamp": "2026-08-25T18:10:00Z"}


def test_g12_reconstructs_complete_frozen_a_decision_basis_and_handover(engine) -> None:
    with Session(engine) as session, session.begin():
        _decision(session)
        basis = reconstruct_decision_basis(session, "DEC-A01")
        assert basis.decision.record_id == "DEC-A01"
        assert dict(basis.decision.fields) == {
            "decision_record_id": "DEC-A01", "change_case_id": "CHG-A01", "assessment_baseline_id": "BL-A01",
            "overlay_revision_id": "OV-A01", "impact_execution_id": "IAX-A01", "required_authority_level": "Standard",
            "current_authority_level": "Standard", "outcome": "Authorised for Downstream Processing",
            "rationale": "Decision package is complete, substantive authorisation blockers are absent, and Standard authority is sufficient.",
            "decision_authority": "Standard Decision Authority A", "decision_timestamp": _dt("2026-08-25T20:00:00Z")}
        assert [(item.record_id, dict(item.fields)) for item in basis.scope_items] == [("DEC-A01:CI-A01:r1", {
            "decision_record_id": "DEC-A01", "change_item_id": "CI-A01", "change_item_revision": "r1"})]
        assert [(item.record_id, dict(item.fields)) for item in basis.support_assessments] == [
            (f"DSA-A0{i}", {"decision_support_assessment_id": f"DSA-A0{i}", "decision_record_id": "DEC-A01", "assessment_id": f"ASM-A0{i}"})
            for i in range(1, 5)]
        assert basis.decision_conditions == ()

        assert dict(basis.execution.fields) == {"impact_execution_id": "IAX-A01", "change_case_id": "CHG-A01",
            "assessment_baseline_id": "BL-A01", "overlay_revision_id": "OV-A01", "rule_set_version": "RRR-v0.1",
            "execution_timestamp": _dt("2026-08-25T19:25:00Z"), "execution_status": "Completed", "routing_status": "Completed"}
        assert dict(basis.baseline.fields) == {"assessment_baseline_id": "BL-A01", "change_case_id": "CHG-A01",
            "snapshot_timestamp": _dt("2026-08-25T19:10:00Z"), "configuration_context_id": "CFG-001",
            "effectivity_context": {"effectivity_type": "Planned Engineering Effective Date", "planned_effective_date": "2026-11-01"},
            "rule_set_version": "RRR-v0.1", "created_at": _dt("2026-08-25T19:10:00Z")}
        expected_members = [
            ("BM-A01-01", "Product Version", "PV-002", "A.1", "PDS-PV-002-A1"),
            ("BM-A01-02", "Product Version", "PV-003", "A.1", "PDS-PV-003-A1"),
            ("BM-A01-03", "Product Structure Occurrence", "PSO-002", "PSO-002@2026-08-25T18:00:00Z", "PDS-PSO-002"),
            ("BM-A01-04", "Configuration Context", "CFG-001", "Complete@2026-08-25", "CFG-001"),
            ("BM-A01-05", "Applicability Rule", "APP-001", "v1", "APP-001"),
            ("BM-A01-06", "Effectivity Specification", "EFF-001", "2026-11-01", "EFF-001"),
            ("BM-A01-07", "Requirement", "REQ-001", "r1", "REQSRC-001"),
            ("BM-A01-08", "Requirement", "REQ-002", "r1", "REQSRC-002"),
            ("BM-A01-09", "Requirement", "REQ-003", "r1", "REQSRC-003"),
            ("BM-A01-10", "Requirement", "REQ-004", "r1", "REQSRC-004")]
        assert [(member.record_id, member.fields["object_type"], member.fields["object_id"], member.fields["object_revision_or_state_token"], member.fields["source_identifier"])
                for member in basis.baseline_members] == expected_members
        canonical = read_canonical_baseline_snapshots()
        expected_payloads = {(item.object_type, item.object_id): item.snapshot_payload for item in canonical.values()}
        for member in basis.baseline_members:
            assert member.fields["assessment_baseline_id"] == "BL-A01"
            assert member.fields["snapshot_payload"] == expected_payloads[(member.fields["object_type"], member.fields["object_id"])]

        assert dict(basis.overlay.fields) == {"overlay_revision_id": "OV-A01", "change_case_id": "CHG-A01", "created_at": _dt("2026-08-25T19:20:00Z")}
        assert [(item.record_id, dict(item.fields)) for item in basis.overlay_membership] == [("OV-A01:CI-A01:r1", {
            "overlay_revision_id": "OV-A01", "change_item_id": "CI-A01", "change_item_revision": "r1"})]
        assert [(item.record_id, dict(item.fields)) for item in basis.overlay_local_objects] == [("OVOBJ-A01-PV", {
            "overlay_revision_id": "OV-A01", "overlay_local_object_id": "OVOBJ-A01-PV", "object_type": "Product Version",
            "source_change_item_id": "CI-A01", "source_change_item_revision": "r1",
            "state_payload": {"product_element_id": "PE-003", "proposed_revision": "B", "proposed_iteration": "1",
                "supersedes_product_version_id": "PV-003", "material_characteristic": "MC-A-01",
                "validated_configuration_scope": 'CoolingType = "Liquid"', "intended_function_change": False}})]
        assert [(item.record_id, dict(item.fields)) for item in basis.change_item_revisions] == [("CI-A01:r1", {
            "change_item_id": "CI-A01", "change_item_revision": "r1", "change_case_id": "CHG-A01", "action": "Revise Product State",
            "target_type": "Product Version", "target_id": "PV-003", "current_state_reference": {"product_version_id": "PV-003", "revision": "A", "iteration": "1"},
            "proposed_state_payload": {"product_element_id": "PE-003", "proposed_revision": "B", "proposed_iteration": "1", "supersedes_product_version_id": "PV-003",
                "material_characteristic": "MC-A-01", "validated_configuration_scope": 'CoolingType = "Liquid"', "intended_function_change": False},
            "reason": "Frozen synthetic change.", "owner": "Change Owner A", "configuration_context_id": "CFG-001",
            "intended_effectivity": {"effectivity_type": "Planned Engineering Effective Date", "planned_effective_date": "2026-11-01"}, "revision_created_at": _dt("2026-08-25T19:02:00Z")})]

        expected_assessments = [
            ("Product Engineering", "Proposed material characteristic changes, but intended function and declared configuration scope remain unchanged.", "Product Engineer A", "2026-08-25T19:40:00Z"),
            ("Validation", "Predecessor validation evidence is accepted as applicable to the proposed successor for this bounded synthetic change.", "Validation Engineer A", "2026-08-25T19:42:00Z"),
            ("Manufacturing", "Predecessor manufacturing evidence is accepted as applicable to the proposed successor for this bounded synthetic change.", "Manufacturing Engineer A", "2026-08-25T19:44:00Z"),
            ("Purchasing/Cost", "Supplier/cost impact is documented and non-blocking.", "Purchasing/Cost Assessor A", "2026-08-25T19:46:00Z")]
        for index, (domain, statement, assessor, completed_at) in enumerate(expected_assessments, 1):
            fields = _by_id(basis.assessments)[f"ASM-A0{index}"]
            assert dict(fields) == {"assessment_id": f"ASM-A0{index}", "change_case_id": "CHG-A01", "origin_impact_execution_id": "IAX-A01",
                "domain": domain, "assessment_state": "Complete", "relevance": "Relevant", "disposition": "No Objection", "impact_statement": statement,
                "assessor": assessor, "completed_at": _dt(completed_at), "is_locked": True}
        assert [(item.fields["assessment_id"], item.fields["impact_candidate_id"]) for item in basis.assessment_impact_links] == [(f"ASM-A0{i}", f"IC-A0{i}") for i in range(1, 5)]
        assert [(item.record_id, item.fields["assessment_id"], item.fields["requirement_id"], item.fields["conclusion"]) for item in basis.requirement_conclusions] == [
            ("ARC-A01", "ASM-A01", "REQ-001", "Satisfied"), ("ARC-A02", "ASM-A02", "REQ-002", "Satisfied"), ("ARC-A03", "ASM-A03", "REQ-003", "Satisfied")]
        assert all(item.fields["assessment_id"] != "ASM-A04" for item in basis.requirement_conclusions)
        expected_evidence = {
            "AEU-A01": _evidence_snapshot("EV-003", "Engineering Review", "SYN-ENG-A-001", "REQ-001", "Current functional interfaces are acceptable in the defined synthetic configuration.", "2026-08-17", "Synthetic Product Engineering Function", "EVSRC-003"),
            "AEU-A02": _evidence_snapshot("EV-001", "Validation Result", "SYN-VAL-A-001", "REQ-002", "Current state meets the defined synthetic validation criterion.", "2026-08-15", "Synthetic Validation Function", "EVSRC-001"),
            "AEU-A03": _evidence_snapshot("EV-002", "Manufacturing Review", "SYN-MFG-A-001", "REQ-003", "Current state is compatible with the defined synthetic manufacturing route.", "2026-08-16", "Synthetic Manufacturing Function", "EVSRC-002"),
            "AEU-A04": _evidence_snapshot("EV-004", "Supplier/Cost Review", "SYN-COST-A-001", None, "Supplier-origin change has a documented non-blocking synthetic cost impact.", "2026-08-18", "Synthetic Purchasing/Cost Function", "EVSRC-004")}
        for index, use in enumerate(basis.evidence_uses, 1):
            fields = use.fields
            evidence_id = ("EV-003", "EV-001", "EV-002", "EV-004")[index - 1]
            assert (use.record_id, fields["assessment_id"], fields["evidence_record_id"], fields["evaluated_product_version_reference"], fields["transferability_conclusion"], fields["evidence_state_token"]) == (f"AEU-A0{index}", f"ASM-A0{index}", evidence_id, "OVOBJ-A01-PV", "Accepted as Applicable", f"{evidence_id}@2026-08-25T18:10:00Z")
            assert fields["evidence_snapshot_payload"] == expected_evidence[use.record_id]

        handover = derive_handover_view(session, "DEC-A01")
        assert handover is not None
        assert (handover.decision_record_id, handover.authorised_change_items, handover.proposed_product_state_action, handover.proposed_product_state_reference, handover.applicability_constraint, handover.planned_engineering_effective_date, handover.decision_conditions) == ("DEC-A01", ("CI-A01:r1",), "Revise Product State", "OVOBJ-A01-PV", 'CoolingType = "Liquid"', "2026-11-01", ())
        tables = set(inspect(session.bind).get_table_names())
        assert "handover_views" not in tables and "historical_reconstructions" not in tables


def test_it15_reconstruction_ignores_live_evidence_mutation(engine) -> None:
    with Session(engine) as session, session.begin():
        _decision(session)
        before = reconstruct_decision_basis(session, "DEC-A01")
        session.get(EvidenceRecord, "EV-003").result = "later mutable live result"
        session.flush()
        assert reconstruct_decision_basis(session, "DEC-A01") == before


@pytest.mark.parametrize("scenario", ["B", "C"])
def test_handover_is_absent_for_case_without_authorised_decision(engine, scenario: str) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, scenario)
        assert session.scalar(select(DecisionRecord.decision_record_id).where(DecisionRecord.change_case_id == f"CHG-{scenario}01")) is None
        assert derive_case_handover_view(session, f"CHG-{scenario}01") is None
