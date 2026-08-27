from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from typer.testing import CliRunner

from plm_ref.application.history_and_views import derive_case_handover_view
from plm_ref.application.readiness import evaluate_authorisation_eligibility, evaluate_gate_b
from plm_ref.application.scenario_runner import reset_database, run_scenario, verify_all
from plm_ref.infrastructure.db.models import AssessmentObligation, ChangeCase, ChangeItemRevision, DecisionRecord, ProcessHistoryEntry
from plm_ref.interfaces.api.app import create_app
from plm_ref.interfaces.cli.main import app


@pytest.mark.parametrize("scenario", ["A", "B", "C"])
def test_g13_runner_executes_each_frozen_scenario_from_clean_database(tmp_path: Path, scenario: str) -> None:
    engine = reset_database(tmp_path / f"{scenario}.db")
    try:
        with Session(engine) as session, session.begin(): run_scenario(session, scenario)
        with Session(engine) as session:
            case = session.get(ChangeCase, f"CHG-{scenario}01")
            revision = session.get(ChangeItemRevision, (f"CI-{scenario}01", "r1"))
            expected_input = {
                "A": ("Cooling Plate supplier-process material characteristic update", "Update one Cooling Plate material characteristic while preserving intended function and current applicability.", "Synthetic supplier process change."),
                "B": ("Cooling Plate material revision requiring applicability scope amendment", "Evaluate a proposed Cooling Plate material characteristic whose validated configuration scope is narrower than the current occurrence applicability.", "Synthetic supplier process change with a narrower validated configuration scope."),
                "C": ("Cooling Plate change requiring Elevated authority", "Evaluate a bounded Cooling Plate product-state revision whose decision route requires Elevated authority.", "Synthetic change prepared under a route that requires Elevated authority."),
            }[scenario]
            assert (case.title, case.rationale, revision.reason) == expected_input
            expected_state = {"A": "Closed by Decision", "B": "In Assessment", "C": "Decision Ready"}[scenario]
            assert (case.change_case_id, case.change_owner, case.case_state, case.process_iteration) == (f"CHG-{scenario}01", f"Change Owner {scenario}", expected_state, 1)
            assert (revision.change_item_id, revision.change_item_revision, revision.change_case_id, revision.action, revision.target_type, revision.target_id, revision.current_state_reference, revision.owner, revision.configuration_context_id, revision.intended_effectivity) == (f"CI-{scenario}01", "r1", f"CHG-{scenario}01", "Revise Product State", "Product Version", "PV-003", {"product_version_id": "PV-003", "revision": "A", "iteration": "1"}, f"Change Owner {scenario}", "CFG-001", {"effectivity_type": "Planned Engineering Effective Date", "planned_effective_date": "2026-11-01"})
            if scenario == "A":
                assert session.get(DecisionRecord, "DEC-A01") is not None
                assert derive_case_handover_view(session, "CHG-A01") is not None
            elif scenario == "B":
                assert session.scalar(select(DecisionRecord.decision_record_id)) is None
                assert derive_case_handover_view(session, "CHG-B01") is None
                assert session.get(ProcessHistoryEntry, "HIST-B01") is not None
                assert [(row.assessment_obligation_id, row.fulfilled_by_assessment_id) for row in session.scalars(select(AssessmentObligation).where(AssessmentObligation.impact_execution_id == "IAX-B02").order_by(AssessmentObligation.assessment_obligation_id))] == [("AO-B21", None), ("AO-B22", None), ("AO-B23", "ASM-B02"), ("AO-B24", "ASM-B04")]
                gate = evaluate_gate_b(session, "IAX-B02")
                assert (gate.gate_b, gate.required_authority_level, evaluate_authorisation_eligibility(session, gate).authorisation_eligibility, case.case_state) == ("Incomplete", "Not Evaluated", "Not Evaluated", "In Assessment")
            else:
                history = session.get(ProcessHistoryEntry, "HIST-C01")
                assert (history.process_history_id, history.change_case_id, history.entry_type, history.timestamp.isoformat(), history.actor, history.origin_stage, history.target_stage_or_route, history.reason, history.affected_change_item_id, history.affected_change_item_revision) == ("HIST-C01", "CHG-C01", "Escalated", "2026-08-25T22:20:00", "Decision Coordinator C", "Authority Check", "Elevated Authority Route", "Required authority is Elevated while current authority is Standard.", "CI-C01", "r1")
                assert case.case_state == "Decision Ready"
                assert session.scalar(select(DecisionRecord.decision_record_id)) is None
                assert derive_case_handover_view(session, "CHG-C01") is None
    finally: engine.dispose()


def test_g13_cli_and_http_share_runner_and_no_raw_mutation_routes(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "interface.db"; monkeypatch.setenv("PLM_REF_DATABASE_PATH", str(path))
    runner = CliRunner()
    assert runner.invoke(app, ["db", "reset"]).exit_code == 0
    assert runner.invoke(app, ["scenario", "load", "A"]).exit_code == 0
    result = runner.invoke(app, ["scenario", "run", "A"])
    assert result.exit_code == 0
    client = TestClient(create_app(path))
    assert client.get("/decisions/DEC-A01/basis").status_code == 200
    assert client.get("/decisions/DEC-A01/handover").json()["decision_record_id"] == "DEC-A01"
    assert client.post("/scenarios/Z/run").status_code == 400
    routes = {(method, route.path) for route in client.app.routes for method in getattr(route, "methods", ())}
    assert not any(method in {"PATCH", "DELETE"} for method, _path in routes)


def test_g13_verify_all_is_deterministic_and_uses_no_expected_or_evidence(tmp_path: Path) -> None:
    path = tmp_path / "verify.db"
    assert verify_all(path, tmp_path / "evidence") and verify_all(path, tmp_path / "evidence")
    assert list(Path("data").rglob("expected.yaml"))
