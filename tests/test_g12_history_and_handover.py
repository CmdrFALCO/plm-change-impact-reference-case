from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from plm_ref.application.decision import persist_terminal_decision
from plm_ref.application.history_and_views import derive_handover_view, reconstruct_decision_basis
from plm_ref.application.source_projection import load_shared_source_fixture
from plm_ref.domain.errors import HistoricalReconstructionError
from plm_ref.infrastructure.db.models import DecisionRecord, EvidenceRecord
from plm_ref.infrastructure.db.session import create_sqlite_engine
from test_g07_assessment import _complete_scenario
from test_g11_terminal_decision import _command


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


def test_g12_reconstructs_exact_decision_basis_and_handover(engine) -> None:
    with Session(engine) as session, session.begin():
        _decision(session)
        basis = reconstruct_decision_basis(session, "DEC-A01")
        assert basis.decision.fields["change_case_id"] == "CHG-A01"
        assert [item.record_id for item in basis.change_item_revisions] == ["CI-A01:r1"]
        assert basis.baseline.record_id == "BL-A01"
        assert {item.record_id for item in basis.overlay_local_objects} == {"OVOBJ-A01-PV"}
        assert basis.execution.record_id == "IAX-A01"
        assert [item.record_id for item in basis.assessments] == ["ASM-A01", "ASM-A02", "ASM-A03", "ASM-A04"]
        assert [item.record_id for item in basis.evidence_uses] == ["AEU-A01", "AEU-A02", "AEU-A03", "AEU-A04"]
        assert not basis.decision_conditions
        handover = derive_handover_view(session, "DEC-A01")
        assert (handover.authorised_change_items, handover.proposed_product_state_action,
            handover.proposed_product_state_reference, handover.applicability_constraint,
            handover.planned_engineering_effective_date, handover.decision_conditions) == (
            ("CI-A01:r1",), "Revise Product State", "OVOBJ-A01-PV", 'CoolingType = "Liquid"', "2026-11-01", ())
        tables = set(inspect(session.bind).get_table_names())
        assert "handover_views" not in tables and "historical_reconstructions" not in tables


def test_it15_reconstruction_ignores_live_evidence_mutation(engine) -> None:
    with Session(engine) as session, session.begin():
        _decision(session)
        before = reconstruct_decision_basis(session, "DEC-A01")
        session.get(EvidenceRecord, "EV-003").result = "later mutable live result"
        session.flush()
        assert reconstruct_decision_basis(session, "DEC-A01") == before


def test_handover_absent_without_authorised_decision(engine) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, "B")
        _complete_scenario(session, "C")
        assert session.scalar(select(DecisionRecord.decision_record_id).where(
            DecisionRecord.change_case_id.in_(("CHG-B01", "CHG-C01")))) is None
        with pytest.raises(HistoricalReconstructionError):
            derive_handover_view(session, "DEC-B01")
