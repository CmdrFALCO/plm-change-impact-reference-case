from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from plm_ref.application.decision import (
    DecisionCommand, DecisionConditionInput, DecisionScopeInput, DecisionSupportInput,
    persist_terminal_decision,
)
from plm_ref.application.source_projection import load_shared_source_fixture
from plm_ref.infrastructure.db.models import (
    ChangeCase, DecisionCondition, DecisionRecord, DecisionScopeItem, DecisionSupportAssessment,
)
from plm_ref.infrastructure.db.session import create_sqlite_engine
from test_g07_assessment import _complete_scenario, _dt


@pytest.fixture
def engine(tmp_path: Path):
    path = tmp_path / "g11.db"
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


def _command(**overrides) -> DecisionCommand:
    values = dict(decision_record_id="DEC-A01", change_case_id="CHG-A01", assessment_baseline_id="BL-A01",
        overlay_revision_id="OV-A01", impact_execution_id="IAX-A01",
        outcome="Authorised for Downstream Processing",
        rationale="Decision package is complete, substantive authorisation blockers are absent, and Standard authority is sufficient.",
        decision_authority="Standard Decision Authority A", decision_timestamp=_dt("2026-08-25T20:00:00Z"),
        scope_items=(DecisionScopeInput("CI-A01", "r1"),),
        support_assessments=tuple(DecisionSupportInput(f"DSA-A0{i}", f"ASM-A0{i}") for i in range(1, 5)),
        conditions=())
    values.update(overrides)
    return DecisionCommand(**values)


def test_g11_scenario_a_persists_exact_terminal_decision_and_closes_case(engine) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, "A")
        assert session.scalar(select(DecisionRecord.decision_record_id)) is None
        record = persist_terminal_decision(session, _command())
        assert (record.decision_record_id, record.change_case_id, record.assessment_baseline_id,
            record.overlay_revision_id, record.impact_execution_id, record.required_authority_level,
            record.current_authority_level, record.outcome, record.rationale, record.decision_authority,
            record.decision_timestamp) == ("DEC-A01", "CHG-A01", "BL-A01", "OV-A01", "IAX-A01",
            "Standard", "Standard", "Authorised for Downstream Processing",
            "Decision package is complete, substantive authorisation blockers are absent, and Standard authority is sufficient.",
            "Standard Decision Authority A", _dt("2026-08-25T20:00:00Z"))
        assert list(session.execute(select(DecisionScopeItem.change_item_id, DecisionScopeItem.change_item_revision))) == [("CI-A01", "r1")]
        assert list(session.scalars(select(DecisionSupportAssessment.assessment_id).order_by(
            DecisionSupportAssessment.decision_support_assessment_id))) == ["ASM-A01", "ASM-A02", "ASM-A03", "ASM-A04"]
        assert session.scalar(select(DecisionCondition.decision_condition_id)) is None
        case = session.get(ChangeCase, "CHG-A01")
        assert (case.case_state, case.closed_at) == ("Closed by Decision", _dt("2026-08-25T20:00:00Z").replace(tzinfo=None))


@pytest.mark.parametrize("command_override", [
    {"scope_items": ()},
    {"scope_items": (DecisionScopeInput("CI-X", "r1"),)},
    {"support_assessments": (DecisionSupportInput("DSA-A01", "ASM-A01"),)},
    {"conditions": (DecisionConditionInput("DC-A01", "x", "x", "Pre-release", "x"),)},
])
def test_terminal_decision_validation_fails_atomically(engine, command_override) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, "A")
        with pytest.raises(ValueError):
            persist_terminal_decision(session, _command(**command_override))
        assert session.scalar(select(DecisionRecord.decision_record_id)) is None
        assert session.get(ChangeCase, "CHG-A01").case_state != "Closed by Decision"


def test_authorised_with_conditions_requires_child_condition(engine) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, "A")
        with pytest.raises(ValueError):
            persist_terminal_decision(session, _command(outcome="Authorised with Conditions"))
        assert session.scalar(select(DecisionRecord.decision_record_id)) is None


def test_duplicate_and_sqlite_mutations_are_rejected(engine) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, "A")
        persist_terminal_decision(session, _command())
        with pytest.raises(ValueError):
            persist_terminal_decision(session, _command())
        with pytest.raises(IntegrityError):
            session.execute(text("UPDATE decision_records SET rationale = 'x' WHERE decision_record_id = 'DEC-A01'"))
        session.rollback()
