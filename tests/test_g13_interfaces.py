from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from typer.testing import CliRunner

from plm_ref.application.history_and_views import derive_case_handover_view
from plm_ref.application.scenario_runner import reset_database, run_scenario, verify_all
from plm_ref.infrastructure.db.models import AssessmentObligation, DecisionRecord, ProcessHistoryEntry
from plm_ref.interfaces.api.app import create_app
from plm_ref.interfaces.cli.main import app


@pytest.mark.parametrize("scenario", ["A", "B", "C"])
def test_g13_runner_executes_each_frozen_scenario_from_clean_database(tmp_path: Path, scenario: str) -> None:
    engine = reset_database(tmp_path / f"{scenario}.db")
    try:
        with Session(engine) as session, session.begin(): run_scenario(session, scenario)
        with Session(engine) as session:
            if scenario == "A":
                assert session.get(DecisionRecord, "DEC-A01") is not None
                assert derive_case_handover_view(session, "CHG-A01") is not None
            elif scenario == "B":
                assert session.scalar(select(DecisionRecord.decision_record_id)) is None
                assert derive_case_handover_view(session, "CHG-B01") is None
                assert session.get(ProcessHistoryEntry, "HIST-B01") is not None
                assert [(row.assessment_obligation_id, row.fulfilled_by_assessment_id) for row in session.scalars(select(AssessmentObligation).where(AssessmentObligation.impact_execution_id == "IAX-B02").order_by(AssessmentObligation.assessment_obligation_id))] == [("AO-B21", None), ("AO-B22", None), ("AO-B23", "ASM-B02"), ("AO-B24", "ASM-B04")]
            else:
                assert session.get(ProcessHistoryEntry, "HIST-C01") is not None
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
    assert verify_all(path) and verify_all(path)
    assert not list(Path("data").rglob("expected.yaml"))
    assert not Path("evidence").exists()
