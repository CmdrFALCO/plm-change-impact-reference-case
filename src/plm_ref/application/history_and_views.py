"""Frozen INC-12 immutable historical and Handover query projections."""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from plm_ref.domain.errors import HistoricalReconstructionError
from plm_ref.infrastructure.db.models import (
    Assessment, AssessmentEvidenceUse, AssessmentImpactLink, AssessmentBaseline,
    AssessmentRequirementConclusion, BaselineMember, ChangeCase, ChangeItemRevision,
    DecisionCondition, DecisionRecord, DecisionScopeItem, DecisionSupportAssessment,
    ImpactCandidate, ImpactExecution, OverlayChangeItemMembership, OverlayLocalObject,
    OverlayRevision,
)


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class RecordView:
    record_id: str
    fields: Mapping[str, Any]


@dataclass(frozen=True)
class DecisionBasisView:
    decision: RecordView
    scope_items: tuple[RecordView, ...]
    change_item_revisions: tuple[RecordView, ...]
    execution: RecordView
    baseline: RecordView
    baseline_members: tuple[RecordView, ...]
    overlay: RecordView
    overlay_membership: tuple[RecordView, ...]
    overlay_local_objects: tuple[RecordView, ...]
    support_assessments: tuple[RecordView, ...]
    assessments: tuple[RecordView, ...]
    assessment_impact_links: tuple[RecordView, ...]
    requirement_conclusions: tuple[RecordView, ...]
    evidence_uses: tuple[RecordView, ...]
    decision_conditions: tuple[RecordView, ...]


@dataclass(frozen=True)
class HandoverView:
    decision_record_id: str
    authorised_change_items: tuple[str, ...]
    proposed_product_state_action: str
    proposed_product_state_reference: str
    applicability_constraint: str | None
    planned_engineering_effective_date: str | None
    decision_conditions: tuple[RecordView, ...]


def _view(record: Any, record_id: str) -> RecordView:
    return RecordView(record_id, MappingProxyType({column.name: _freeze(getattr(record, column.name))
        for column in record.__table__.columns}))


def reconstruct_decision_basis(session: Session, decision_record_id: str) -> DecisionBasisView:
    decision = session.get(DecisionRecord, decision_record_id)
    if decision is None:
        raise HistoricalReconstructionError("Decision Record does not exist")
    execution = session.get(ImpactExecution, decision.impact_execution_id)
    baseline = session.get(AssessmentBaseline, decision.assessment_baseline_id)
    overlay = session.get(OverlayRevision, decision.overlay_revision_id)
    case = session.get(ChangeCase, decision.change_case_id)
    if (case is None or execution is None or baseline is None or overlay is None
            or (execution.change_case_id, execution.assessment_baseline_id, execution.overlay_revision_id)
            != (decision.change_case_id, decision.assessment_baseline_id, decision.overlay_revision_id)
            or baseline.change_case_id != decision.change_case_id or overlay.change_case_id != decision.change_case_id):
        raise HistoricalReconstructionError("Decision execution/baseline/overlay lineage crosses Change Case")
    scope = tuple(session.scalars(select(DecisionScopeItem).where(
        DecisionScopeItem.decision_record_id == decision_record_id).order_by(
        DecisionScopeItem.change_item_id, DecisionScopeItem.change_item_revision)))
    revisions = []
    membership = {(row.change_item_id, row.change_item_revision) for row in session.scalars(select(
        OverlayChangeItemMembership).where(OverlayChangeItemMembership.overlay_revision_id == overlay.overlay_revision_id))}
    for item in scope:
        revision = session.get(ChangeItemRevision, (item.change_item_id, item.change_item_revision))
        if revision is None or revision.change_case_id != decision.change_case_id or (item.change_item_id, item.change_item_revision) not in membership:
            raise HistoricalReconstructionError("Decision Scope Item has invalid historical lineage")
        revisions.append(revision)
    support = tuple(session.scalars(select(DecisionSupportAssessment).where(
        DecisionSupportAssessment.decision_record_id == decision_record_id).order_by(
        DecisionSupportAssessment.decision_support_assessment_id)))
    assessments = []
    for item in support:
        assessment = session.get(Assessment, item.assessment_id)
        if assessment is None or assessment.change_case_id != decision.change_case_id or not assessment.is_locked:
            raise HistoricalReconstructionError("Decision Support Assessment has invalid historical lineage")
        assessments.append(assessment)
    assessment_ids = [assessment.assessment_id for assessment in assessments]
    links = tuple(session.scalars(select(AssessmentImpactLink).where(
        AssessmentImpactLink.assessment_id.in_(assessment_ids))))
    for link in links:
        candidate = session.get(ImpactCandidate, link.impact_candidate_id)
        if candidate is None or candidate.impact_execution_id != execution.impact_execution_id:
            raise HistoricalReconstructionError("Assessment Impact Link crosses Decision execution")
    conclusions = tuple(session.scalars(select(AssessmentRequirementConclusion).where(
        AssessmentRequirementConclusion.assessment_id.in_(assessment_ids)).order_by(
        AssessmentRequirementConclusion.assessment_requirement_conclusion_id)))
    evidence = tuple(session.scalars(select(AssessmentEvidenceUse).where(
        AssessmentEvidenceUse.assessment_id.in_(assessment_ids)).order_by(
        AssessmentEvidenceUse.assessment_evidence_use_id)))
    return DecisionBasisView(
        _view(decision, decision.decision_record_id), tuple(_view(row, f"{row.decision_record_id}:{row.change_item_id}:{row.change_item_revision}") for row in scope),
        tuple(_view(row, f"{row.change_item_id}:{row.change_item_revision}") for row in revisions), _view(execution, execution.impact_execution_id),
        _view(baseline, baseline.assessment_baseline_id), tuple(_view(row, row.baseline_member_id) for row in session.scalars(select(BaselineMember).where(BaselineMember.assessment_baseline_id == baseline.assessment_baseline_id).order_by(BaselineMember.baseline_member_id))),
        _view(overlay, overlay.overlay_revision_id), tuple(_view(row, f"{row.overlay_revision_id}:{row.change_item_id}:{row.change_item_revision}") for row in session.scalars(select(OverlayChangeItemMembership).where(OverlayChangeItemMembership.overlay_revision_id == overlay.overlay_revision_id))),
        tuple(_view(row, row.overlay_local_object_id) for row in session.scalars(select(OverlayLocalObject).where(OverlayLocalObject.overlay_revision_id == overlay.overlay_revision_id).order_by(OverlayLocalObject.overlay_local_object_id))),
        tuple(_view(row, row.decision_support_assessment_id) for row in support), tuple(_view(row, row.assessment_id) for row in assessments),
        tuple(RecordView(f"{row.assessment_id}:{row.impact_candidate_id}", MappingProxyType({"assessment_id": row.assessment_id, "impact_candidate_id": row.impact_candidate_id})) for row in links),
        tuple(_view(row, row.assessment_requirement_conclusion_id) for row in conclusions), tuple(_view(row, row.assessment_evidence_use_id) for row in evidence),
        tuple(_view(row, row.decision_condition_id) for row in session.scalars(select(DecisionCondition).where(DecisionCondition.decision_record_id == decision_record_id))),
    )


def derive_handover_view(session: Session, decision_record_id: str) -> HandoverView | None:
    basis = reconstruct_decision_basis(session, decision_record_id)
    outcome = basis.decision.fields["outcome"]
    if outcome not in {"Authorised for Downstream Processing", "Authorised with Conditions"}:
        return None
    revisions = basis.change_item_revisions
    if len(revisions) != 1 or revisions[0].fields["action"] != "Revise Product State":
        raise HistoricalReconstructionError("frozen Handover scope requires one Revise Product State")
    payload = revisions[0].fields["proposed_state_payload"]
    overlay_objects = [item for item in basis.overlay_local_objects if item.fields["object_type"] == "Product Version"]
    if len(overlay_objects) != 1:
        raise HistoricalReconstructionError("frozen Handover requires one overlay-local Product Version")
    return HandoverView(decision_record_id,
        tuple(f"{item.fields['change_item_id']}:{item.fields['change_item_revision']}" for item in basis.scope_items),
        revisions[0].fields["action"], overlay_objects[0].record_id,
        payload.get("validated_configuration_scope"), revisions[0].fields["intended_effectivity"].get("planned_effective_date"), basis.decision_conditions)


def derive_case_handover_view(session: Session, change_case_id: str) -> HandoverView | None:
    """Return the authorised Handover for a case, or deterministic absence."""
    decisions = tuple(session.scalars(select(DecisionRecord).where(
        DecisionRecord.change_case_id == change_case_id,
        DecisionRecord.outcome.in_((
            "Authorised for Downstream Processing", "Authorised with Conditions",
        )),
    ).order_by(DecisionRecord.decision_record_id)))
    if not decisions:
        return None
    if len(decisions) != 1:
        raise HistoricalReconstructionError("Change Case has ambiguous authorised Decisions")
    return derive_handover_view(session, decisions[0].decision_record_id)
