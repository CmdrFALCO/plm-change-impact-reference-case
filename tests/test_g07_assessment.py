from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from plm_ref.application.assessment import (
    AssessmentCompletionInput,
    EvidenceUseInput,
    RequirementConclusionInput,
    complete_assessment,
    update_assessment_impact_statement,
)
from plm_ref.application.routing import route_impact_execution
from plm_ref.application.source_projection import load_shared_source_fixture
from plm_ref.domain.errors import AssessmentCompletionError, ImmutableRecordError
from plm_ref.infrastructure.db.models import (
    Assessment,
    AssessmentEvidenceUse,
    AssessmentImpactLink,
    AssessmentObligation,
    AssessmentRequirementConclusion,
    AssessmentReuseClassification,
    EvidenceRecord,
    ImpactCandidate,
    ImpactExecution,
)
from plm_ref.infrastructure.db.session import create_sqlite_engine
from test_g05_impact_execution import _execute_frozen, _execution, _prepare_initial_scenario


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@pytest.fixture
def engine(tmp_path: Path):
    database_path = tmp_path / "g07.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{database_path}")
    command.upgrade(config, "head")
    db = create_sqlite_engine(database_path)
    with Session(db) as session, session.begin():
        load_shared_source_fixture(session)
    try:
        yield db
    finally:
        db.dispose()


EVIDENCE_BY_INDEX = {1: "EV-003", 2: "EV-001", 3: "EV-002", 4: "EV-004"}
DOMAIN_BY_INDEX = {1: "Product Engineering", 2: "Validation", 3: "Manufacturing", 4: "Purchasing/Cost"}
ASSESSOR_ROLE = {1: "Product Engineer", 2: "Validation Engineer", 3: "Manufacturing Engineer", 4: "Purchasing/Cost Assessor"}
REQUIREMENTS = {"A": {1: "REQ-001", 2: "REQ-002", 3: "REQ-003"}, "B": {1: "REQ-004", 2: "REQ-002", 3: "REQ-003"}, "C": {1: "REQ-001", 2: "REQ-002", 3: "REQ-003"}}
COMPLETED = {
    "A": ["2026-08-25T19:40:00Z", "2026-08-25T19:42:00Z", "2026-08-25T19:44:00Z", "2026-08-25T19:46:00Z"],
    "B": ["2026-08-25T20:50:00Z", "2026-08-25T20:52:00Z", "2026-08-25T20:54:00Z", "2026-08-25T20:56:00Z"],
    "C": ["2026-08-25T22:10:00Z", "2026-08-25T22:12:00Z", "2026-08-25T22:14:00Z", "2026-08-25T22:16:00Z"],
}
STATEMENTS = {
    "A": [
        "Proposed material characteristic changes, but intended function and declared configuration scope remain unchanged.",
        "Predecessor validation evidence is accepted as applicable to the proposed successor for this bounded synthetic change.",
        "Predecessor manufacturing evidence is accepted as applicable to the proposed successor for this bounded synthetic change.",
        "Supplier/cost impact is documented and non-blocking.",
    ],
    "B": [
        'The proposed state is validated only for `CoolingType = "Liquid" AND PackFamily = "LongRange"`, while `PSO-002` currently applies to all `CoolingType = "Liquid"` configurations. The occurrence applicability must therefore be changed explicitly before the proposal can proceed to terminal decision.',
        "Validation evidence is acceptable for the bounded technical state evaluated in the first execution.",
        "Manufacturing evidence is acceptable for the bounded technical state evaluated in the first execution.",
        "Supplier/cost impact remains documented and non-blocking.",
    ],
}
STATEMENTS["C"] = STATEMENTS["A"]


def _snapshot(e: EvidenceRecord) -> dict[str, object]:
    timestamp = e.extraction_timestamp.replace(tzinfo=timezone.utc) if e.extraction_timestamp.tzinfo is None else e.extraction_timestamp
    return {"evidence_record_id": e.evidence_record_id, "evidence_type": e.evidence_type,
        "reference": e.reference, "applicable_product_version_id": e.applicable_product_version_id,
        "configuration_context_id": e.configuration_context_id, "requirement_id": e.requirement_id,
        "result": e.result, "issue_date": e.issue_date.isoformat(), "validity_state": e.validity_state,
        "provider": e.provider, "superseded_by_evidence_id": e.superseded_by_evidence_id,
        "source_class": e.source_class, "source_identifier": e.source_identifier,
        "extraction_timestamp": timestamp.isoformat().replace("+00:00", "Z")}


def _prepare(session: Session, scenario: str) -> None:
    _prepare_initial_scenario(session, scenario)
    _execute_frozen(session, _execution(scenario))
    assert route_impact_execution(session, f"IAX-{scenario}01").routing_status == "Completed"


def _input(scenario: str, index: int, *, assessment_id: str | None = None,
           conclusions: tuple[RequirementConclusionInput, ...] | None = None,
           evidence: tuple[EvidenceUseInput, ...] | None = None) -> AssessmentCompletionInput:
    req = REQUIREMENTS[scenario].get(index)
    conclusion = "Not Satisfied" if scenario == "B" and index == 1 else "Satisfied"
    return AssessmentCompletionInput(
        assessment_id or f"ASM-{scenario}0{index}", f"CHG-{scenario}01", f"IAX-{scenario}01",
        DOMAIN_BY_INDEX[index], "Relevant", "No Objection with Conditions" if scenario == "B" and index == 1 else "No Objection",
        STATEMENTS[scenario][index - 1], f"{ASSESSOR_ROLE[index]} {scenario}", _dt(COMPLETED[scenario][index - 1]),
        (f"IC-{scenario}0{index}",),
        conclusions if conclusions is not None else (() if req is None else (RequirementConclusionInput(f"ARC-{scenario}0{index}", req, conclusion),)),
        evidence if evidence is not None else (EvidenceUseInput(f"AEU-{scenario}0{index}", EVIDENCE_BY_INDEX[index], f"OVOBJ-{scenario}01-PV", "Accepted as Applicable", f"{EVIDENCE_BY_INDEX[index]}@2026-08-25T18:10:00Z"),),
        (f"AO-{scenario}0{index}",),
    )


def _complete_scenario(session: Session, scenario: str) -> None:
    _prepare(session, scenario)
    for index in range(1, 5):
        complete_assessment(session, _input(scenario, index))


@pytest.mark.parametrize("scenario", ["A", "B", "C"])
def test_frozen_scenario_assessments_complete_exactly(engine, scenario: str) -> None:
    with Session(engine) as session, session.begin():
        _complete_scenario(session, scenario)
    with Session(engine) as session:
        assessments = list(session.scalars(select(Assessment).order_by(Assessment.assessment_id)))
        assert len(assessments) == 4
        for index, assessment in enumerate(assessments, 1):
            expected = _input(scenario, index)
            assert (assessment.assessment_id, assessment.change_case_id, assessment.origin_impact_execution_id,
                    assessment.domain, assessment.assessment_state, assessment.relevance, assessment.disposition,
                    assessment.impact_statement, assessment.assessor, assessment.completed_at, assessment.is_locked) == (
                    expected.assessment_id, expected.change_case_id, expected.origin_impact_execution_id,
                    expected.domain, "Complete", expected.relevance, expected.disposition,
                    expected.impact_statement, expected.assessor, expected.completed_at.replace(tzinfo=None), True)
        assert list(session.execute(select(AssessmentImpactLink.assessment_id, AssessmentImpactLink.impact_candidate_id).order_by(AssessmentImpactLink.assessment_id))) == [(f"ASM-{scenario}0{i}", f"IC-{scenario}0{i}") for i in range(1, 5)]
        conclusions = list(session.execute(select(AssessmentRequirementConclusion.assessment_requirement_conclusion_id, AssessmentRequirementConclusion.assessment_id, AssessmentRequirementConclusion.requirement_id, AssessmentRequirementConclusion.conclusion).order_by(AssessmentRequirementConclusion.assessment_id)))
        assert conclusions == [(f"ARC-{scenario}0{i}", f"ASM-{scenario}0{i}", REQUIREMENTS[scenario][i], "Not Satisfied" if scenario == "B" and i == 1 else "Satisfied") for i in range(1, 4)]
        uses = list(session.scalars(select(AssessmentEvidenceUse).order_by(AssessmentEvidenceUse.assessment_id)))
        assert len(uses) == 4
        for index, use in enumerate(uses, 1):
            evidence_id = EVIDENCE_BY_INDEX[index]
            assert (use.assessment_evidence_use_id, use.assessment_id, use.evidence_record_id,
                    use.evaluated_product_version_reference, use.transferability_conclusion, use.evidence_state_token) == (
                    f"AEU-{scenario}0{index}", f"ASM-{scenario}0{index}", evidence_id,
                    f"OVOBJ-{scenario}01-PV", "Accepted as Applicable", f"{evidence_id}@2026-08-25T18:10:00Z")
            assert use.evidence_snapshot_payload == _snapshot(session.get(EvidenceRecord, evidence_id))
        assert list(session.execute(select(AssessmentObligation.assessment_obligation_id, AssessmentObligation.fulfilled_by_assessment_id).order_by(AssessmentObligation.assessment_obligation_id))) == [(f"AO-{scenario}0{i}", f"ASM-{scenario}0{i}") for i in range(1, 5)]
        assert list(session.scalars(select(ImpactCandidate.candidate_state).order_by(ImpactCandidate.impact_candidate_id))) == ["Assessed"] * 4


def _reject_sql(engine, statement: str, parameters: dict[str, object]) -> None:
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(text(statement), parameters)


def test_it06_locked_assessment_and_children_are_immutable(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare(session, "B")
        complete_assessment(session, _input("B", 2))
    with Session(engine) as session, pytest.raises(ImmutableRecordError):
        update_assessment_impact_statement(session, "ASM-B02", "changed")
    _reject_sql(engine, "UPDATE assessments SET assessor='x' WHERE assessment_id='ASM-B02'", {})
    _reject_sql(engine, "DELETE FROM assessments WHERE assessment_id='ASM-B02'", {})
    for table, insert_sql, update_sql in (
        ("assessment_impact_links", "INSERT INTO assessment_impact_links VALUES ('ASM-B02','IC-B01')", "UPDATE assessment_impact_links SET impact_candidate_id='IC-B01' WHERE assessment_id='ASM-B02'"),
        ("assessment_requirement_conclusions", "INSERT INTO assessment_requirement_conclusions VALUES ('ARC-X','ASM-B02','REQ-001','Satisfied')", "UPDATE assessment_requirement_conclusions SET conclusion='Not Demonstrated' WHERE assessment_id='ASM-B02'"),
        ("assessment_evidence_uses", "INSERT INTO assessment_evidence_uses VALUES ('AEU-X','ASM-B02','EV-002','OVOBJ-B01-PV','Accepted as Applicable','x','{}')", "UPDATE assessment_evidence_uses SET evidence_state_token='x' WHERE assessment_id='ASM-B02'"),
    ):
        _reject_sql(engine, insert_sql, {})
        _reject_sql(engine, update_sql, {})
        _reject_sql(engine, f"DELETE FROM {table} WHERE assessment_id='ASM-B02'", {})
    _reject_sql(engine, "UPDATE assessment_obligations SET fulfilled_by_assessment_id=NULL WHERE assessment_obligation_id='AO-B02'", {})
    _reject_sql(engine, "UPDATE assessment_obligations SET fulfilled_by_assessment_id='ASM-X' WHERE assessment_obligation_id='AO-B02'", {})


@pytest.mark.parametrize("failure", ["missing-conclusion", "missing-evidence", "null-transferability", "not-applicable"])
def test_failed_completion_is_atomic(engine, failure: str) -> None:
    with Session(engine) as session, session.begin():
        _prepare(session, "A")
        base = _input("A", 2, assessment_id=f"ASM-FAIL-{failure}")
        conclusions = () if failure == "missing-conclusion" else base.requirement_conclusions
        if failure == "missing-evidence": evidence = ()
        elif failure == "null-transferability": evidence = (EvidenceUseInput("AEU-FAIL", "EV-001", "OVOBJ-A01-PV", None, "token"),)
        elif failure == "not-applicable": evidence = (EvidenceUseInput("AEU-FAIL", "EV-001", "OVOBJ-A01-PV", "Not Applicable to Proposed State", "token"),)
        else: evidence = base.evidence_uses
        with pytest.raises(AssessmentCompletionError):
            complete_assessment(session, AssessmentCompletionInput(base.assessment_id, base.change_case_id,
                base.origin_impact_execution_id, base.domain, base.relevance, base.disposition, base.impact_statement,
                base.assessor, base.completed_at, base.impact_candidate_ids, conclusions, evidence, base.fulfil_obligation_ids))
        assert session.get(Assessment, base.assessment_id) is None
        assert session.scalar(select(AssessmentImpactLink).where(AssessmentImpactLink.assessment_id == base.assessment_id)) is None
        assert session.get(AssessmentObligation, "AO-A02").fulfilled_by_assessment_id is None
        assert session.get(ImpactCandidate, "IC-A02").candidate_state == "Assessment Planned"


def test_duplicate_conclusion_and_incompatible_impact_links_are_rejected(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare(session, "A")
        _prepare(session, "B")
        duplicate = (RequirementConclusionInput("ARC-D1", "REQ-002", "Satisfied"),
                     RequirementConclusionInput("ARC-D2", "REQ-002", "Not Demonstrated"))
        with pytest.raises(AssessmentCompletionError):
            complete_assessment(session, _input("A", 2, assessment_id="ASM-DUP", conclusions=duplicate))
        wrong_domain = _input("A", 2, assessment_id="ASM-DOMAIN")
        wrong_domain = AssessmentCompletionInput(wrong_domain.assessment_id, wrong_domain.change_case_id,
            wrong_domain.origin_impact_execution_id, wrong_domain.domain, wrong_domain.relevance,
            wrong_domain.disposition, wrong_domain.impact_statement, wrong_domain.assessor,
            wrong_domain.completed_at, ("IC-A01",), wrong_domain.requirement_conclusions,
            wrong_domain.evidence_uses, wrong_domain.fulfil_obligation_ids)
        with pytest.raises(AssessmentCompletionError):
            complete_assessment(session, wrong_domain)
        cross_execution = AssessmentCompletionInput("ASM-CROSS", "CHG-A01", "IAX-A01", "Validation",
            "Relevant", "No Objection", "cross", "assessor", _dt("2026-08-25T19:42:00Z"),
            ("IC-B02",), (RequirementConclusionInput("ARC-CROSS", "REQ-002", "Satisfied"),),
            (EvidenceUseInput("AEU-CROSS", "EV-001", "OVOBJ-A01-PV", "Accepted as Applicable", "token"),),
            ("AO-A02",))
        with pytest.raises(AssessmentCompletionError):
            complete_assessment(session, cross_execution)
        assert session.get(Assessment, "ASM-DUP") is None
        assert session.get(Assessment, "ASM-DOMAIN") is None
        assert session.get(Assessment, "ASM-CROSS") is None


def test_evidence_snapshot_survives_live_evidence_mutation(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare(session, "A")
        complete_assessment(session, _input("A", 2))
        before = dict(session.get(AssessmentEvidenceUse, "AEU-A02").evidence_snapshot_payload)
    with Session(engine) as session, session.begin():
        session.get(EvidenceRecord, "EV-001").result = "later live result"
    with Session(engine) as session:
        assert session.get(AssessmentEvidenceUse, "AEU-A02").evidence_snapshot_payload == before
        assert session.get(AssessmentRequirementConclusion, "ARC-A02").conclusion == "Satisfied"


def test_retained_fixture_allows_future_null_assignment_then_locks_it(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare(session, "B")
        complete_assessment(session, _input("B", 2))
        source = session.get(ImpactExecution, "IAX-B01")
        session.add(ImpactExecution(impact_execution_id="IAX-LATER", change_case_id="CHG-B01",
            assessment_baseline_id=source.assessment_baseline_id, overlay_revision_id=source.overlay_revision_id,
            rule_set_version=source.rule_set_version, execution_timestamp=_dt("2026-08-25T21:10:00Z"),
            execution_status="Completed", routing_status="Completed"))
        session.flush()
        session.add(AssessmentObligation(assessment_obligation_id="AO-LATER", impact_execution_id="IAX-LATER",
            impact_candidate_id=None, domain="Validation", requirement_id="REQ-002", mandatory=True,
            fulfilled_by_assessment_id=None, routing_rule_reference="RRR-02"))
        session.add(AssessmentReuseClassification(assessment_reuse_classification_id="ARU-TEST",
            assessment_id="ASM-B02", target_impact_execution_id="IAX-LATER", classification="Retained", rationale="fixture"))
    with engine.begin() as connection:
        connection.execute(text("UPDATE assessment_obligations SET fulfilled_by_assessment_id='ASM-B02' WHERE assessment_obligation_id='AO-LATER'"))
    _reject_sql(engine, "UPDATE assessment_obligations SET fulfilled_by_assessment_id=NULL WHERE assessment_obligation_id='AO-LATER'", {})
    _reject_sql(engine, "UPDATE assessment_obligations SET fulfilled_by_assessment_id='ASM-B03' WHERE assessment_obligation_id='AO-LATER'", {})
