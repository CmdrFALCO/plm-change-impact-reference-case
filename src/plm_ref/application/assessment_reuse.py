"""Frozen INC-09 assessment reuse and retained fulfilment boundary."""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from plm_ref.domain.errors import AssessmentReuseError
from plm_ref.infrastructure.db.models import (
    Assessment, AssessmentEvidenceUse, AssessmentImpactLink, AssessmentObligation,
    AssessmentRequirementConclusion, AssessmentReuseClassification, ChangeItemRevision,
    ImpactCandidate, ImpactExecution, OverlayChangeItemMembership, OverlayLocalObject,
)


RATIONALES = {
    "ASM-B01": "The original Product Engineering assessment concluded that applicability was not aligned; the new overlay changes that exact applicability state and requires a new assessment.",
    "ASM-B02": "The bounded validation conclusion remains applicable to the unchanged proposed Product Version technical state; the added applicability Change Item does not alter the validated characteristic itself.",
    "ASM-B03": "Manufacturing assessment must confirm that the narrowed applicability does not alter the declared manufacturing applicability assumptions.",
    "ASM-B04": "Supplier/cost conclusion is unchanged by the added occurrence-applicability Change Item.",
}


@dataclass(frozen=True)
class RetainedFulfilment:
    assessment_obligation_id: str
    assessment_id: str


def _applicability_targets(session: Session, execution: ImpactExecution) -> set[str]:
    keys = session.execute(select(OverlayChangeItemMembership.change_item_id,
        OverlayChangeItemMembership.change_item_revision).where(
        OverlayChangeItemMembership.overlay_revision_id == execution.overlay_revision_id))
    return {revision.target_id for key in keys
        if (revision := session.get(ChangeItemRevision, key)) is not None
        and revision.action == "Change Applicability"}


def _linked_candidates(session: Session, assessment_id: str) -> list[ImpactCandidate]:
    return list(session.scalars(select(ImpactCandidate).join(AssessmentImpactLink,
        AssessmentImpactLink.impact_candidate_id == ImpactCandidate.impact_candidate_id).where(
        AssessmentImpactLink.assessment_id == assessment_id)))


def _same_product_state(session: Session, historical: ImpactExecution, target: ImpactExecution) -> bool:
    def revise_membership(execution: ImpactExecution) -> set[tuple[str, str]]:
        keys = session.execute(select(OverlayChangeItemMembership.change_item_id,
            OverlayChangeItemMembership.change_item_revision).where(
            OverlayChangeItemMembership.overlay_revision_id == execution.overlay_revision_id))
        return {key for key in keys if (revision := session.get(ChangeItemRevision, key)) is not None
            and revision.action == "Revise Product State"}
    def states(execution: ImpactExecution) -> list[dict]:
        return list(session.scalars(select(OverlayLocalObject.state_payload).where(
            OverlayLocalObject.overlay_revision_id == execution.overlay_revision_id,
            OverlayLocalObject.object_type == "Product Version")))
    old, new = states(historical), states(target)
    return (revise_membership(historical) == revise_membership(target)
        and len(old) == len(new) == 1 and old[0] == new[0])


def classify_assessment_reuse(session: Session, target_impact_execution_id: str) -> tuple[AssessmentReuseClassification, ...]:
    target = session.get(ImpactExecution, target_impact_execution_id)
    if target is None or target.execution_status != "Completed" or target.routing_status != "Completed":
        raise AssessmentReuseError("target execution must be completed and routed")
    if session.scalar(select(AssessmentReuseClassification.assessment_reuse_classification_id).where(
        AssessmentReuseClassification.target_impact_execution_id == target_impact_execution_id).limit(1)) is not None:
        raise AssessmentReuseError("target execution is already classified")
    changed_occurrences = _applicability_targets(session, target)
    results: list[AssessmentReuseClassification] = []
    assessments = list(session.scalars(select(Assessment).where(
        Assessment.change_case_id == target.change_case_id,
        Assessment.origin_impact_execution_id != target.impact_execution_id,
        Assessment.assessment_state == "Complete", Assessment.is_locked.is_(True)).order_by(Assessment.assessment_id)))
    for assessment in assessments:
        historical = session.get(ImpactExecution, assessment.origin_impact_execution_id)
        candidates = _linked_candidates(session, assessment.assessment_id)
        linked_changed_occurrence = any(c.candidate_type == "Product Structure Occurrence" and c.candidate_reference in changed_occurrences for c in candidates)
        req004_not_satisfied = session.scalar(select(AssessmentRequirementConclusion.conclusion).where(
            AssessmentRequirementConclusion.assessment_id == assessment.assessment_id,
            AssessmentRequirementConclusion.requirement_id == "REQ-004")) == "Not Satisfied"
        classification = None
        if assessment.domain == "Product Engineering" and linked_changed_occurrence and req004_not_satisfied:
            classification = "Invalidated"
        elif assessment.domain == "Manufacturing" and linked_changed_occurrence and historical is not None and _same_product_state(session, historical, target):
            classification = "Revalidation Required"
        elif assessment.domain in {"Validation", "Purchasing/Cost"} and historical is not None and _same_product_state(session, historical, target):
            classification = "Retained"
        if classification is None:
            continue
        try:
            rationale = RATIONALES[assessment.assessment_id]
        except KeyError as exc:
            raise AssessmentReuseError("no frozen reuse rationale exists") from exc
        record = AssessmentReuseClassification(
            assessment_reuse_classification_id="ARU-" + assessment.assessment_id[4:],
            assessment_id=assessment.assessment_id, target_impact_execution_id=target.impact_execution_id,
            classification=classification, rationale=rationale)
        session.add(record); results.append(record)
    session.flush()
    return tuple(results)


def fulfil_from_retained_assessments(session: Session, assignments: tuple[RetainedFulfilment, ...]) -> None:
    if not assignments:
        raise AssessmentReuseError("retained fulfilment assignment set is empty")
    with session.begin_nested():
        for assignment in assignments:
            obligation = session.get(AssessmentObligation, assignment.assessment_obligation_id)
            assessment = session.get(Assessment, assignment.assessment_id)
            if obligation is None or assessment is None:
                raise AssessmentReuseError("obligation or historical Assessment does not exist")
            target = session.get(ImpactExecution, obligation.impact_execution_id)
            classification = session.scalar(select(AssessmentReuseClassification).where(
                AssessmentReuseClassification.assessment_id == assessment.assessment_id,
                AssessmentReuseClassification.target_impact_execution_id == obligation.impact_execution_id))
            if classification is None or classification.classification != "Retained":
                raise AssessmentReuseError("historical Assessment is not explicitly Retained")
            if target is None or assessment.change_case_id != target.change_case_id:
                raise AssessmentReuseError("historical Assessment crosses Change Case")
            if assessment.assessment_state != "Complete" or not assessment.is_locked:
                raise AssessmentReuseError("historical Assessment is not Complete and locked")
            if assessment.domain != obligation.domain:
                raise AssessmentReuseError("historical Assessment domain is incompatible")
            if obligation.fulfilled_by_assessment_id is not None:
                raise AssessmentReuseError("target obligation is already fulfilled")
            if obligation.requirement_id is not None and session.scalar(select(
                AssessmentRequirementConclusion.assessment_requirement_conclusion_id).where(
                AssessmentRequirementConclusion.assessment_id == assessment.assessment_id,
                AssessmentRequirementConclusion.requirement_id == obligation.requirement_id)) is None:
                raise AssessmentReuseError("historical Assessment lacks matching Requirement Conclusion")
            evidence = list(session.scalars(select(AssessmentEvidenceUse).where(
                AssessmentEvidenceUse.assessment_id == assessment.assessment_id)))
            if not evidence or not any(use.transferability_conclusion != "Not Applicable to Proposed State" for use in evidence):
                raise AssessmentReuseError("historical Assessment lacks compatible Evidence Use")
            obligation.fulfilled_by_assessment_id = assessment.assessment_id
        session.flush()
