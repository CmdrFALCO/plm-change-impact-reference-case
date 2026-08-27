from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from plm_ref.application.oracle_verification import compare_scenario, load_expected
from plm_ref.application.scenario_runner import reset_database, run_scenario, verify_all


@pytest.mark.parametrize("scenario", ["A", "B", "C"])
def test_g14_independent_oracle_compares_clean_frozen_runs(tmp_path: Path, scenario: str) -> None:
    engine = reset_database(tmp_path / f"{scenario}.db")
    try:
        with Session(engine) as session, session.begin(): run_scenario(session, scenario)
        with Session(engine) as session:
            actual, diffs = compare_scenario(session, scenario)
        assert actual["scenario"] == scenario and diffs == []
    finally: engine.dispose()


def test_g14_comparator_reports_wrong_scalar_missing_field_and_extra_row(tmp_path: Path) -> None:
    engine = reset_database(tmp_path / "A.db")
    try:
        with Session(engine) as session, session.begin(): run_scenario(session, "A")
        with Session(engine) as session:
            expected = deepcopy(load_expected("A")); expected["tables"]["change_cases"][0]["case_state"] = "Wrong"
            assert any(diff["path"].endswith("case_state") for diff in compare_scenario(session, "A", expected)[1])
            expected = deepcopy(load_expected("A")); expected["tables"]["change_cases"][0]["missing_frozen_field"] = "required"
            assert compare_scenario(session, "A", expected)[1]
            expected = deepcopy(load_expected("A")); expected["tables"]["decision_records"].append({"decision_record_id": "EXTRA", "change_case_id": "CHG-A01", "outcome": "Rejected"})
            assert any("length" in diff["path"] for diff in compare_scenario(session, "A", expected)[1])
    finally: engine.dispose()


def test_g14_evidence_is_deterministic_and_has_six_pass_groups(tmp_path: Path) -> None:
    database, evidence = tmp_path / "verify.db", tmp_path / "evidence"
    assert verify_all(database, evidence)
    first = {path.name: path.read_bytes() for path in evidence.iterdir()}
    assert verify_all(database, evidence)
    assert {path.name: path.read_bytes() for path in evidence.iterdir()} == first
    groups = json.loads((evidence / "integrity_results.json").read_text())
    assert all(groups.values()) and len(groups) == 6
    assert {path.name for path in evidence.iterdir()} == {
        "scenario_a_actual.json", "scenario_a_diff.json", "scenario_b_actual.json", "scenario_b_diff.json",
        "scenario_c_actual.json", "scenario_c_diff.json", "decision_DEC-A01_basis.json", "integrity_results.json", "verification_summary.md"}
