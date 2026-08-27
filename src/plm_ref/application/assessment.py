"""Frozen INC-07 Assessment completion boundary."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from plm_ref.domain.errors import AssessmentCompletionError
from plm_ref.infrastructure.db.guards import assert_assessment_mutable
from plm_ref.infrastructure.db.models import (
    Assessment, AssessmentEvidenceUse, AssessmentImpactLink,
    AssessmentObligation, AssessmentRequirementConclusion, BaselineMember,
    EvidenceRecord, ImpactCandidate, ImpactExecution, OverlayLocalObject,
)


@dataclass(frozen=True)
class RequirementConclusionInput:
    assessment_requirement_conclusion_id: str
    requirement_id: str
    conclusion: str


@dataclass(frozen=True)
class EvidenceUseInput:
    assessment_evidence_use_id: str
    evidence_record_id: str
    evaluated_product_version_reference: str
    transferability_conclusion: str | None
    evidence_state_token: str


@dataclass(frozen=True)
class AssessmentCompletionInput:
    assessment_id: str
    change_case_id: str
    origin_impact_execution_id: str
    domain: str
    relevance: str
    disposition: str
    impact_statement: str
    assessor: str
    completed_at: datetime
    impact_candidate_ids: tuple[str, ...]
    requirement_conclusions: tuple[RequirementConclusionInput, ...]
    evidence_uses: tuple[EvidenceUseInput, ...]
    fulfil_obligation_ids: tuple[str, ...]


def _snapshot(evidence: EvidenceRecord) -> dict[str, object]:
    extraction_timestamp = evidence.extraction_timestamp
    if extraction_timestamp.tzinfo is None:
        extraction_timestamp = extraction_timestamp.replace(tzinfo=timezone.utc)
    return {
        "evidence_record_id": evidence.evidence_record_id, "evidence_type": evidence.evidence_type,
        "reference": evidence.reference, "applicable_product_version_id": evidence.applicable_product_version_id,
        "configuration_context_id": evidence.configuration_context_id, "requirement_id": evidence.requirement_id,
        "result": evidence.result, "issue_date": evidence.issue_date.isoformat(),
        "validity_state": evidence.validity_state, "provider": evidence.provider,
        "superseded_by_evidence_id": evidence.superseded_by_evidence_id, "source_class": evidence.source_class,
        "source_identifier": evidence.source_identifier,
        "extraction_timestamp": extraction_timestamp.isoformat().replace("+00:00", "Z"),
    }


def _assert_evaluated_reference(session: Session, execution: ImpactExecution, reference: str) -> None:
    baseline = session.scalar(select(BaselineMember.baseline_member_id).where(
        BaselineMember.assessment_baseline_id == execution.assessment_baseline_id,
        BaselineMember.object_type == "Product Version", BaselineMember.object_id == reference))
    overlay = session.scalar(select(OverlayLocalObject.overlay_local_object_id).where(
        OverlayLocalObject.overlay_revision_id == execution.overlay_revision_id,
        OverlayLocalObject.object_type == "Product Version", OverlayLocalObject.overlay_local_object_id == reference))
    if baseline is None and overlay is None:
        raise AssessmentCompletionError("Evidence Use evaluated Product Version is outside execution lineage")


def complete_assessment(session: Session, data: AssessmentCompletionInput) -> Assessment:
    """Create, validate and lock one Assessment atomically."""
    with session.begin_nested():
        execution = session.get(ImpactExecution, data.origin_impact_execution_id)
        if execution is None or execution.change_case_id != data.change_case_id:
            raise AssessmentCompletionError("Assessment origin execution is not case-local")
        if session.get(Assessment, data.assessment_id) is not None:
            raise AssessmentCompletionError("Assessment already exists")
        obligations = list(session.scalars(select(AssessmentObligation).where(
            AssessmentObligation.assessment_obligation_id.in_(data.fulfil_obligation_ids))))
        if len(obligations) != len(set(data.fulfil_obligation_ids)) or not obligations:
            raise AssessmentCompletionError("Assessment must fulfil explicit routed obligations")
        for obligation in obligations:
            if (obligation.impact_execution_id != execution.impact_execution_id or obligation.domain != data.domain
                    or obligation.fulfilled_by_assessment_id is not None):
                raise AssessmentCompletionError("Assessment obligation is incompatible")
        assessment = Assessment(assessment_id=data.assessment_id, change_case_id=data.change_case_id,
            origin_impact_execution_id=data.origin_impact_execution_id, domain=data.domain,
            assessment_state="In Progress", relevance=data.relevance, disposition=data.disposition,
            impact_statement=data.impact_statement, assessor=data.assessor, completed_at=None, is_locked=False)
        session.add(assessment); session.flush()
        candidate_ids = set(data.impact_candidate_ids)
        for candidate_id in candidate_ids:
            candidate = session.get(ImpactCandidate, candidate_id)
            if candidate is None or candidate.impact_execution_id != execution.impact_execution_id or candidate.affected_domain != data.domain:
                raise AssessmentCompletionError("Assessment Impact Link crosses execution or domain")
            session.add(AssessmentImpactLink(assessment_id=assessment.assessment_id, impact_candidate_id=candidate_id))
        conclusions = {item.requirement_id: item for item in data.requirement_conclusions}
        if len(conclusions) != len(data.requirement_conclusions):
            raise AssessmentCompletionError("duplicate Requirement Conclusion")
        for item in data.requirement_conclusions:
            session.add(AssessmentRequirementConclusion(assessment_requirement_conclusion_id=item.assessment_requirement_conclusion_id,
                assessment_id=assessment.assessment_id, requirement_id=item.requirement_id, conclusion=item.conclusion))
        for item in data.evidence_uses:
            evidence = session.get(EvidenceRecord, item.evidence_record_id)
            if evidence is None:
                raise AssessmentCompletionError("Evidence Record does not exist")
            _assert_evaluated_reference(session, execution, item.evaluated_product_version_reference)
            if evidence.applicable_product_version_id != item.evaluated_product_version_reference and item.transferability_conclusion is None:
                raise AssessmentCompletionError("predecessor Evidence requires transferability")
            session.add(AssessmentEvidenceUse(assessment_evidence_use_id=item.assessment_evidence_use_id,
                assessment_id=assessment.assessment_id, evidence_record_id=evidence.evidence_record_id,
                evaluated_product_version_reference=item.evaluated_product_version_reference,
                transferability_conclusion=item.transferability_conclusion,
                evidence_state_token=item.evidence_state_token, evidence_snapshot_payload=_snapshot(evidence)))
        session.flush()
        usable = session.scalar(select(AssessmentEvidenceUse.assessment_evidence_use_id).where(
            AssessmentEvidenceUse.assessment_id == assessment.assessment_id,
            or_(AssessmentEvidenceUse.transferability_conclusion.is_(None),
                AssessmentEvidenceUse.transferability_conclusion != "Not Applicable to Proposed State")).limit(1))
        for obligation in obligations:
            if obligation.requirement_id is not None and obligation.requirement_id not in conclusions:
                raise AssessmentCompletionError("mandatory obligation lacks Requirement Conclusion")
            if obligation.impact_candidate_id is not None and obligation.impact_candidate_id not in candidate_ids:
                raise AssessmentCompletionError("mandatory obligation lacks compatible Impact Link")
            if usable is None:
                raise AssessmentCompletionError("mandatory obligation lacks Evidence Use")
            obligation.fulfilled_by_assessment_id = assessment.assessment_id
        session.flush()
        for candidate_id in candidate_ids:
            outstanding = session.scalar(select(AssessmentObligation.assessment_obligation_id).where(
                AssessmentObligation.impact_candidate_id == candidate_id, AssessmentObligation.mandatory.is_(True),
                AssessmentObligation.fulfilled_by_assessment_id.is_(None)).limit(1))
            if outstanding is None:
                session.get(ImpactCandidate, candidate_id).candidate_state = "Assessed"
        assessment.assessment_state = "Complete"; assessment.completed_at = data.completed_at; assessment.is_locked = True
        session.flush()
    return assessment


def update_assessment_impact_statement(session: Session, assessment_id: str, impact_statement: str) -> Assessment:
    assessment = assert_assessment_mutable(session, assessment_id)
    assessment.impact_statement = impact_statement
    session.flush()
    return assessment
