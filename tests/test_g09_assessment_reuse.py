from __future__ import annotations

import json
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import select
from sqlalchemy.orm import Session

from plm_ref.application.assessment_reuse import (
    RetainedFulfilment, classify_assessment_reuse, fulfil_from_retained_assessments,
)
from plm_ref.application.baseline import BaselineReuseInputs, reuse_assessment_baseline
from plm_ref.application.change_case import create_change_item
from plm_ref.application.gate_a import evaluate_gate_a
from plm_ref.application.overlay import OverlayRevisionInput, create_overlay_revision
from plm_ref.application.routing import route_impact_execution
from plm_ref.application.scope_routing import evaluate_scope_route
from plm_ref.application.source_projection import load_shared_source_fixture
from plm_ref.domain.errors import AssessmentReuseError
from plm_ref.infrastructure.db.models import (
    Assessment, AssessmentEvidenceUse, AssessmentImpactLink, AssessmentObligation,
    AssessmentRequirementConclusion, AssessmentReuseClassification, ChangeCase, ImpactCandidate,
    ImpactExecution,
)
from plm_ref.infrastructure.db.session import create_sqlite_engine
from test_g05_impact_execution import _b02_execution, _execute_frozen
from test_g07_assessment import _complete_scenario, _dt
from test_g08_scope_route import _b02_proposal, _b02_revision, _command


@pytest.fixture
def engine(tmp_path: Path):
    path = tmp_path / "g09.db"
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


def _prepare_second_cycle(session: Session) -> None:
    _complete_scenario(session, "B")
    assert evaluate_scope_route(session, _command()) is not None
    create_change_item(session, _b02_revision(), _b02_proposal())
    assert evaluate_gate_a(session, "CHG-B01").passed
    reuse_assessment_baseline(session, "BL-B01", "CHG-B01", BaselineReuseInputs(
        authoritative_current_state_unchanged=True, baseline_scope_still_sufficient=True,
        configuration_context_still_valid=True, effectivity_context_still_valid=True,
        extraction_basis_still_accepted=True))
    create_overlay_revision(session, "BL-B01", OverlayRevisionInput(
        overlay_revision_id="OV-B02", change_case_id="CHG-B01",
        created_at=_dt("2026-08-25T21:10:00Z")),
        local_object_ids={"CI-B01": "OVOBJ-B02-PV", "CI-B02": "OVOBJ-B02-PSO"})
    _execute_frozen(session, _b02_execution())
    assert route_impact_execution(session, "IAX-B02").routing_status == "Completed"


def _canonical_assessment(session: Session, assessment_id: str) -> str:
    assessment = session.get(Assessment, assessment_id)
    payload = {
        "assessment": {column.name: getattr(assessment, column.name) for column in Assessment.__table__.columns},
        "links": list(session.execute(select(AssessmentImpactLink.assessment_id,
            AssessmentImpactLink.impact_candidate_id).where(AssessmentImpactLink.assessment_id == assessment_id))),
        "conclusions": list(session.execute(select(
            AssessmentRequirementConclusion.assessment_requirement_conclusion_id,
            AssessmentRequirementConclusion.requirement_id,
            AssessmentRequirementConclusion.conclusion).where(
            AssessmentRequirementConclusion.assessment_id == assessment_id).order_by(
            AssessmentRequirementConclusion.assessment_requirement_conclusion_id))),
        "evidence": [{column.name: getattr(use, column.name) for column in AssessmentEvidenceUse.__table__.columns}
            for use in session.scalars(select(AssessmentEvidenceUse).where(
                AssessmentEvidenceUse.assessment_id == assessment_id).order_by(
                AssessmentEvidenceUse.assessment_evidence_use_id))],
    }
    return json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))


def test_it07_exact_reuse_and_retained_fulfilment_preserves_history(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_second_cycle(session)
        execution = session.get(ImpactExecution, "IAX-B02")
        assert (execution.execution_status, execution.routing_status) == ("Completed", "Completed")
        assert list(session.execute(select(ImpactCandidate.impact_candidate_id,
            ImpactCandidate.affected_domain, ImpactCandidate.candidate_reference,
            ImpactCandidate.candidate_state).where(ImpactCandidate.impact_execution_id == "IAX-B02").order_by(
            ImpactCandidate.impact_candidate_id))) == [
            ("IC-B21", "Product Engineering", "OVOBJ-B02-PSO", "Assessment Planned"),
            ("IC-B22", "Manufacturing", "OVOBJ-B02-PSO", "Assessment Planned")]
        obligations = list(session.execute(select(AssessmentObligation.assessment_obligation_id,
            AssessmentObligation.impact_candidate_id, AssessmentObligation.domain,
            AssessmentObligation.requirement_id, AssessmentObligation.fulfilled_by_assessment_id).where(
            AssessmentObligation.impact_execution_id == "IAX-B02").order_by(
            AssessmentObligation.assessment_obligation_id)))
        assert obligations == [("AO-B21", "IC-B21", "Product Engineering", "REQ-004", None),
            ("AO-B22", "IC-B22", "Manufacturing", "REQ-003", None),
            ("AO-B23", None, "Validation", "REQ-002", None),
            ("AO-B24", None, "Purchasing/Cost", None, None)]
        before = {key: _canonical_assessment(session, key)
            for key in ("ASM-B01", "ASM-B02", "ASM-B03", "ASM-B04")}
        classifications = classify_assessment_reuse(session, "IAX-B02")
        assert [(c.assessment_reuse_classification_id, c.assessment_id,
            c.target_impact_execution_id, c.classification, c.rationale) for c in classifications] == [
            ("ARU-B01", "ASM-B01", "IAX-B02", "Invalidated", "The original Product Engineering assessment concluded that applicability was not aligned; the new overlay changes that exact applicability state and requires a new assessment."),
            ("ARU-B02", "ASM-B02", "IAX-B02", "Retained", "The bounded validation conclusion remains applicable to the unchanged proposed Product Version technical state; the added applicability Change Item does not alter the validated characteristic itself."),
            ("ARU-B03", "ASM-B03", "IAX-B02", "Revalidation Required", "Manufacturing assessment must confirm that the narrowed applicability does not alter the declared manufacturing applicability assumptions."),
            ("ARU-B04", "ASM-B04", "IAX-B02", "Retained", "Supplier/cost conclusion is unchanged by the added occurrence-applicability Change Item.")]
        fulfil_from_retained_assessments(session, (RetainedFulfilment("AO-B23", "ASM-B02"),
            RetainedFulfilment("AO-B24", "ASM-B04")))
        assert {key: _canonical_assessment(session, key) for key in before} == before
        assert list(session.execute(select(AssessmentObligation.assessment_obligation_id,
            AssessmentObligation.fulfilled_by_assessment_id).where(
            AssessmentObligation.impact_execution_id == "IAX-B02").order_by(
            AssessmentObligation.assessment_obligation_id))) == [
            ("AO-B21", None), ("AO-B22", None), ("AO-B23", "ASM-B02"), ("AO-B24", "ASM-B04")]
        assert list(session.scalars(select(ImpactCandidate.candidate_state).where(
            ImpactCandidate.impact_execution_id == "IAX-B02").order_by(
            ImpactCandidate.impact_candidate_id))) == ["Assessment Planned", "Assessment Planned"]


@pytest.mark.parametrize(("obligation", "assessment"), [("AO-B21", "ASM-B01"), ("AO-B22", "ASM-B03")])
def test_it08_non_retained_reuse_cannot_fulfil(engine, obligation: str, assessment: str) -> None:
    with Session(engine) as session, session.begin():
        _prepare_second_cycle(session)
        classify_assessment_reuse(session, "IAX-B02")
        with pytest.raises(AssessmentReuseError):
            fulfil_from_retained_assessments(session, (RetainedFulfilment(obligation, assessment),))
        assert session.get(AssessmentObligation, obligation).fulfilled_by_assessment_id is None


def test_missing_or_wrong_target_classification_fails_atomically(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_second_cycle(session)
        with pytest.raises(AssessmentReuseError):
            fulfil_from_retained_assessments(session, (RetainedFulfilment("AO-B23", "ASM-B02"),))
        assert session.get(AssessmentObligation, "AO-B23").fulfilled_by_assessment_id is None
        session.add(AssessmentReuseClassification(assessment_reuse_classification_id="ARU-WRONG",
            assessment_id="ASM-B02", target_impact_execution_id="IAX-B01", classification="Retained", rationale="wrong target fixture"))
        with pytest.raises(AssessmentReuseError):
            fulfil_from_retained_assessments(session, (RetainedFulfilment("AO-B23", "ASM-B02"),))
        assert session.get(AssessmentObligation, "AO-B23").fulfilled_by_assessment_id is None


def test_multi_assignment_failure_rolls_back_prior_retained_update(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_second_cycle(session)
        classify_assessment_reuse(session, "IAX-B02")
        with pytest.raises(AssessmentReuseError):
            fulfil_from_retained_assessments(session, (RetainedFulfilment("AO-B23", "ASM-B02"),
                RetainedFulfilment("AO-B22", "ASM-B03")))
        assert session.get(AssessmentObligation, "AO-B23").fulfilled_by_assessment_id is None
        assert session.get(AssessmentObligation, "AO-B22").fulfilled_by_assessment_id is None


def test_already_fulfilled_target_obligation_fails(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_second_cycle(session)
        classify_assessment_reuse(session, "IAX-B02")
        assignment = RetainedFulfilment("AO-B23", "ASM-B02")
        fulfil_from_retained_assessments(session, (assignment,))
        with pytest.raises(AssessmentReuseError):
            fulfil_from_retained_assessments(session, (assignment,))
        assert session.get(AssessmentObligation, "AO-B23").fulfilled_by_assessment_id == "ASM-B02"


@pytest.mark.parametrize(("obligation", "assessment"), [("AO-B24", "ASM-B02"), ("AO-B23", "ASM-B04")])
def test_retained_domain_mismatch_fails(engine, obligation: str, assessment: str) -> None:
    with Session(engine) as session, session.begin():
        _prepare_second_cycle(session)
        classify_assessment_reuse(session, "IAX-B02")
        with pytest.raises(AssessmentReuseError):
            fulfil_from_retained_assessments(session, (RetainedFulfilment(obligation, assessment),))
        assert session.get(AssessmentObligation, obligation).fulfilled_by_assessment_id is None


def test_retained_requirement_mismatch_fails(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_second_cycle(session)
        classify_assessment_reuse(session, "IAX-B02")
        session.get(AssessmentObligation, "AO-B23").requirement_id = "REQ-003"
        session.flush()
        with pytest.raises(AssessmentReuseError):
            fulfil_from_retained_assessments(session, (RetainedFulfilment("AO-B23", "ASM-B02"),))
        assert session.get(AssessmentObligation, "AO-B23").fulfilled_by_assessment_id is None


@pytest.mark.parametrize(("state", "locked"), [("Submitted", False), ("Complete", False)])
def test_incomplete_or_unlocked_historical_assessment_fails(engine, state: str, locked: bool) -> None:
    with Session(engine) as session, session.begin():
        _prepare_second_cycle(session)
        session.add(Assessment(assessment_id="ASM-FAKE", change_case_id="CHG-B01",
            origin_impact_execution_id="IAX-B01", domain="Validation", assessment_state=state,
            relevance="Relevant", disposition="No Objection", impact_statement="fixture",
            assessor="fixture", completed_at=None, is_locked=locked))
        session.flush()
        session.add(AssessmentReuseClassification(assessment_reuse_classification_id="ARU-FAKE",
            assessment_id="ASM-FAKE", target_impact_execution_id="IAX-B02", classification="Retained", rationale="fixture"))
        with pytest.raises(AssessmentReuseError):
            fulfil_from_retained_assessments(session, (RetainedFulfilment("AO-B23", "ASM-FAKE"),))
        assert session.get(AssessmentObligation, "AO-B23").fulfilled_by_assessment_id is None


def test_cross_case_historical_assessment_fails(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_second_cycle(session)
        session.add(ChangeCase(change_case_id="CHG-X", title="x", trigger="x", rationale="x",
            change_owner="x", case_state="Open", process_iteration=1,
            created_at=_dt("2026-08-25T20:00:00Z"), closed_at=None))
        session.flush()
        session.add(Assessment(assessment_id="ASM-X", change_case_id="CHG-X",
            origin_impact_execution_id="IAX-B01", domain="Validation", assessment_state="Complete",
            relevance="Relevant", disposition="No Objection", impact_statement="fixture",
            assessor="fixture", completed_at=_dt("2026-08-25T20:30:00Z"), is_locked=True))
        session.flush()
        session.add(AssessmentReuseClassification(assessment_reuse_classification_id="ARU-X",
            assessment_id="ASM-X", target_impact_execution_id="IAX-B02", classification="Retained", rationale="fixture"))
        with pytest.raises(AssessmentReuseError):
            fulfil_from_retained_assessments(session, (RetainedFulfilment("AO-B23", "ASM-X"),))
        assert session.get(AssessmentObligation, "AO-B23").fulfilled_by_assessment_id is None


def test_missing_historical_evidence_use_fails(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_second_cycle(session)
        session.add(Assessment(assessment_id="ASM-NO-EV", change_case_id="CHG-B01",
            origin_impact_execution_id="IAX-B01", domain="Purchasing/Cost", assessment_state="Complete",
            relevance="Relevant", disposition="No Objection", impact_statement="fixture",
            assessor="fixture", completed_at=_dt("2026-08-25T20:30:00Z"), is_locked=True))
        session.flush()
        session.add(AssessmentReuseClassification(assessment_reuse_classification_id="ARU-NO-EV",
            assessment_id="ASM-NO-EV", target_impact_execution_id="IAX-B02", classification="Retained", rationale="fixture"))
        with pytest.raises(AssessmentReuseError):
            fulfil_from_retained_assessments(session, (RetainedFulfilment("AO-B24", "ASM-NO-EV"),))
        assert session.get(AssessmentObligation, "AO-B24").fulfilled_by_assessment_id is None


def test_incompatible_historical_evidence_use_fails(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_second_cycle(session)
        session.add(Assessment(assessment_id="ASM-BAD-EV", change_case_id="CHG-B01",
            origin_impact_execution_id="IAX-B01", domain="Purchasing/Cost", assessment_state="Complete",
            relevance="Relevant", disposition="No Objection", impact_statement="fixture",
            assessor="fixture", completed_at=_dt("2026-08-25T20:30:00Z"), is_locked=False))
        session.flush()
        session.add(AssessmentEvidenceUse(assessment_evidence_use_id="AEU-BAD-EV",
            assessment_id="ASM-BAD-EV", evidence_record_id="EV-004",
            evaluated_product_version_reference="OVOBJ-B01-PV",
            transferability_conclusion="Not Applicable to Proposed State",
            evidence_state_token="fixture", evidence_snapshot_payload={"fixture": True}))
        session.flush()
        session.get(Assessment, "ASM-BAD-EV").is_locked = True
        session.flush()
        session.add(AssessmentReuseClassification(assessment_reuse_classification_id="ARU-BAD-EV",
            assessment_id="ASM-BAD-EV", target_impact_execution_id="IAX-B02",
            classification="Retained", rationale="fixture"))
        with pytest.raises(AssessmentReuseError):
            fulfil_from_retained_assessments(session, (RetainedFulfilment("AO-B24", "ASM-BAD-EV"),))
        assert session.get(AssessmentObligation, "AO-B24").fulfilled_by_assessment_id is None
