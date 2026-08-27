"""Frozen INC-10 Gate B and Authorisation Eligibility calculations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from plm_ref.application.change_case import active_proposed_change_scope
from plm_ref.infrastructure.db.models import (
    Assessment, AssessmentEvidenceUse, AssessmentImpactLink, AssessmentObligation,
    AssessmentRequirementConclusion, AssessmentReuseClassification, AssessmentBaseline,
    BaselineMember, ChangeCase, ChangeItemRevision, ImpactCandidate, ImpactExecution, OpenItem,
    OverlayChangeItemMembership, OverlayLocalObject, OverlayRevision, ProcessHistoryEntry,
)
from plm_ref.rules.rrr_v01 import evaluate_rrr06


NOT_EVALUATED = "Not Evaluated"


@dataclass(frozen=True)
class GateBResult:
    impact_execution_id: str
    gate_b: Literal["Complete", "Incomplete"]
    required_authority_level: Literal["Standard", "Elevated"] | str
    failed_predicate: str | None
    rrr_06_evaluated: bool


@dataclass(frozen=True)
class AuthorisationEligibilityResult:
    impact_execution_id: str
    authorisation_eligibility: Literal["Permitted", "Blocked"] | str


def _execution(session: Session, impact_execution_id: str) -> ImpactExecution | None:
    execution = session.get(ImpactExecution, impact_execution_id)
    if execution is None:
        return None
    case = session.get(ChangeCase, execution.change_case_id)
    baseline = session.get(AssessmentBaseline, execution.assessment_baseline_id)
    overlay = session.get(OverlayRevision, execution.overlay_revision_id)
    return execution if (case is not None and baseline is not None and overlay is not None
                         and baseline.change_case_id == execution.change_case_id
                         and overlay.change_case_id == execution.change_case_id) else None


def _overlay_membership(session: Session, execution: ImpactExecution) -> set[tuple[str, str]]:
    return set(session.execute(select(
        OverlayChangeItemMembership.change_item_id,
        OverlayChangeItemMembership.change_item_revision,
    ).where(OverlayChangeItemMembership.overlay_revision_id == execution.overlay_revision_id)))


def _exact_scope_known(session: Session, execution: ImpactExecution) -> bool:
    active = {(revision.change_item_id, revision.change_item_revision)
        for revision in active_proposed_change_scope(session, execution.change_case_id)}
    return _overlay_membership(session, execution) == active


def _scope_revision_route_outstanding(session: Session, execution: ImpactExecution) -> bool:
    # An RRR-05 record is historical once this overlay contains the explicit
    # Change Applicability amendment required for that proposal cycle.
    has_applicability_amendment = False
    for membership in _overlay_membership(session, execution):
        revision = session.get(ChangeItemRevision, membership)
        if revision is not None and revision.action == "Change Applicability":
            has_applicability_amendment = True
            break
    route_exists = session.scalar(select(ProcessHistoryEntry.process_history_id).where(
        ProcessHistoryEntry.change_case_id == execution.change_case_id,
        ProcessHistoryEntry.entry_type == "Scope Revision Required",
    ).limit(1)) is not None and not has_applicability_amendment
    return route_exists


def _evidence_usable_for_assessment(
    session: Session, assessment: Assessment, source_execution: ImpactExecution,
) -> bool:
    uses = list(session.scalars(select(AssessmentEvidenceUse).where(
        AssessmentEvidenceUse.assessment_id == assessment.assessment_id)))
    if not uses:
        return False
    for use in uses:
        if use.transferability_conclusion == "Not Applicable to Proposed State":
            continue
        overlay_object = session.scalar(select(OverlayLocalObject).where(
            OverlayLocalObject.overlay_revision_id == source_execution.overlay_revision_id,
            OverlayLocalObject.overlay_local_object_id == use.evaluated_product_version_reference,
        ))
        if overlay_object is not None:
            if overlay_object.object_type != "Product Version":
                continue
            evidence_product_version = use.evidence_snapshot_payload.get("applicable_product_version_id")
            if evidence_product_version != use.evaluated_product_version_reference and use.transferability_conclusion is None:
                continue
            return True
        baseline = session.scalar(select(BaselineMember.baseline_member_id).where(
            BaselineMember.assessment_baseline_id == source_execution.assessment_baseline_id,
            BaselineMember.object_type == "Product Version",
            BaselineMember.object_id == use.evaluated_product_version_reference,
        ))
        if baseline is not None:
            return True
    return False


def _satisfying_assessment(
    session: Session, execution: ImpactExecution, obligation: AssessmentObligation,
) -> Assessment | None:
    if obligation.fulfilled_by_assessment_id is None:
        return None
    assessment = session.get(Assessment, obligation.fulfilled_by_assessment_id)
    if (assessment is None or assessment.change_case_id != execution.change_case_id
            or assessment.domain != obligation.domain or assessment.assessment_state != "Complete"
            or not assessment.is_locked):
        return None
    source_execution = _execution(session, assessment.origin_impact_execution_id)
    if source_execution is None or source_execution.change_case_id != execution.change_case_id:
        return None
    direct = assessment.origin_impact_execution_id == execution.impact_execution_id
    retained = session.scalar(select(AssessmentReuseClassification.assessment_reuse_classification_id).where(
        AssessmentReuseClassification.assessment_id == assessment.assessment_id,
        AssessmentReuseClassification.target_impact_execution_id == execution.impact_execution_id,
        AssessmentReuseClassification.classification == "Retained",
    ).limit(1)) is not None
    if not direct and not retained:
        return None
    if obligation.impact_candidate_id is not None:
        candidate = session.get(ImpactCandidate, obligation.impact_candidate_id)
        if candidate is None or candidate.impact_execution_id != execution.impact_execution_id:
            return None
        if session.scalar(select(AssessmentImpactLink.assessment_id).where(
            AssessmentImpactLink.assessment_id == assessment.assessment_id,
            AssessmentImpactLink.impact_candidate_id == obligation.impact_candidate_id,
        ).limit(1)) is None:
            return None
    if obligation.requirement_id is not None and session.scalar(select(
        AssessmentRequirementConclusion.assessment_requirement_conclusion_id
    ).where(
        AssessmentRequirementConclusion.assessment_id == assessment.assessment_id,
        AssessmentRequirementConclusion.requirement_id == obligation.requirement_id,
    ).limit(1)) is None:
        return None
    return assessment if _evidence_usable_for_assessment(session, assessment, source_execution) else None


def _mandatory_obligations(session: Session, execution: ImpactExecution) -> list[AssessmentObligation]:
    return list(session.scalars(select(AssessmentObligation).where(
        AssessmentObligation.impact_execution_id == execution.impact_execution_id,
        AssessmentObligation.mandatory.is_(True),
    ).order_by(AssessmentObligation.assessment_obligation_id)))


def _all_mandatory_obligations_satisfied(
    session: Session, execution: ImpactExecution, obligations: list[AssessmentObligation],
) -> bool:
    return all(_satisfying_assessment(session, execution, obligation) is not None for obligation in obligations)


def _mandatory_candidates_covered(
    session: Session, execution: ImpactExecution, obligations: list[AssessmentObligation],
) -> bool:
    candidate_ids = {obligation.impact_candidate_id for obligation in obligations
        if obligation.impact_candidate_id is not None}
    return all(all(_satisfying_assessment(session, execution, obligation) is not None
        for obligation in obligations if obligation.impact_candidate_id == candidate_id)
        for candidate_id in candidate_ids)


def _no_unresolved_decision_open_item(session: Session, execution: ImpactExecution) -> bool:
    return session.scalar(select(OpenItem.open_item_id).where(
        OpenItem.change_case_id == execution.change_case_id,
        OpenItem.blocking_class == "Blocking",
        OpenItem.required_before_stage == "Decision",
        OpenItem.status != "Resolved",
    ).limit(1)) is None


def _required_evidence_criteria_fulfilled(
    session: Session, execution: ImpactExecution, obligations: list[AssessmentObligation],
) -> bool:
    return all(_satisfying_assessment(session, execution, obligation) is not None for obligation in obligations)


def evaluate_gate_b(session: Session, impact_execution_id: str) -> GateBResult:
    """Evaluate frozen pre-authority predicates in their mandated short-circuit order."""
    execution = _execution(session, impact_execution_id)
    if execution is None or execution.execution_status != "Completed":
        return GateBResult(impact_execution_id, "Incomplete", NOT_EVALUATED,
            "impact_execution_completed", False)
    if execution.routing_status != "Completed":
        return GateBResult(impact_execution_id, "Incomplete", NOT_EVALUATED,
            "assessment_routing_completed", False)
    if _scope_revision_route_outstanding(session, execution):
        return GateBResult(impact_execution_id, "Incomplete", NOT_EVALUATED,
            "scope_revision_route_outstanding", False)
    if not _exact_scope_known(session, execution):
        return GateBResult(impact_execution_id, "Incomplete", NOT_EVALUATED,
            "exact_proposed_change_scope_known", False)
    obligations = _mandatory_obligations(session, execution)
    if not _all_mandatory_obligations_satisfied(session, execution, obligations):
        return GateBResult(impact_execution_id, "Incomplete", NOT_EVALUATED,
            "all_mandatory_obligations_satisfied", False)
    if not _mandatory_candidates_covered(session, execution, obligations):
        return GateBResult(impact_execution_id, "Incomplete", NOT_EVALUATED,
            "all_mandatory_impact_candidates_covered", False)
    if not _no_unresolved_decision_open_item(session, execution):
        return GateBResult(impact_execution_id, "Incomplete", NOT_EVALUATED,
            "decision_blocking_open_items_resolved", False)
    if not _required_evidence_criteria_fulfilled(session, execution, obligations):
        return GateBResult(impact_execution_id, "Incomplete", NOT_EVALUATED,
            "required_evidence_criteria_fulfilled", False)
    authority = evaluate_rrr06(session.get(ChangeCase, execution.change_case_id).trigger)
    if authority.required_authority_level is None:
        return GateBResult(impact_execution_id, "Incomplete", NOT_EVALUATED,
            "required_authority_level_is_known", True)
    return GateBResult(impact_execution_id, "Complete", authority.required_authority_level,
        None, True)


def evaluate_authorisation_eligibility(
    session: Session, gate_b: GateBResult,
) -> AuthorisationEligibilityResult:
    """Evaluate substantive blockers only after package completeness is established."""
    if gate_b.gate_b != "Complete":
        return AuthorisationEligibilityResult(gate_b.impact_execution_id, NOT_EVALUATED)
    execution = _execution(session, gate_b.impact_execution_id)
    if execution is None:
        return AuthorisationEligibilityResult(gate_b.impact_execution_id, NOT_EVALUATED)
    for obligation in _mandatory_obligations(session, execution):
        assessment = _satisfying_assessment(session, execution, obligation)
        if assessment is None:
            return AuthorisationEligibilityResult(gate_b.impact_execution_id, "Blocked")
        if assessment.disposition in {"Objection", "Escalation Recommended"}:
            return AuthorisationEligibilityResult(gate_b.impact_execution_id, "Blocked")
        if obligation.requirement_id is not None:
            conclusion = session.scalar(select(AssessmentRequirementConclusion.conclusion).where(
                AssessmentRequirementConclusion.assessment_id == assessment.assessment_id,
                AssessmentRequirementConclusion.requirement_id == obligation.requirement_id,
            ))
            if conclusion in {"Not Satisfied", "Not Demonstrated"}:
                return AuthorisationEligibilityResult(gate_b.impact_execution_id, "Blocked")
    return AuthorisationEligibilityResult(gate_b.impact_execution_id, "Permitted")


def derive_case_state(session: Session, gate_b: GateBResult) -> ChangeCase | None:
    """Apply only the frozen pre-decision case-state derivations."""
    execution = _execution(session, gate_b.impact_execution_id)
    if execution is None:
        return None
    case = session.get(ChangeCase, execution.change_case_id)
    if gate_b.gate_b == "Complete":
        case.case_state = "Decision Ready"
    elif (execution.execution_status == "Completed" and execution.routing_status == "Completed"
          and gate_b.failed_predicate in {"all_mandatory_obligations_satisfied", "all_mandatory_impact_candidates_covered", "required_evidence_criteria_fulfilled"}):
        case.case_state = "In Assessment"
    session.flush()
    return case
