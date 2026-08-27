"""Frozen RRR-05 structured scope-route application service."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from plm_ref.infrastructure.db.models import (
    Assessment, AssessmentImpactLink, AssessmentRequirementConclusion,
    BaselineMember, ChangeItemRevision, ImpactCandidate, ImpactCandidateProvenance,
    ImpactExecution, OverlayChangeItemMembership, OverlayLocalObject, ProcessHistoryEntry,
)
from plm_ref.rules.rrr_v01 import Rrr05Input, evaluate_rrr05, validated_scope_relation


@dataclass(frozen=True)
class ScopeRouteCommand:
    impact_execution_id: str
    process_history_id: str
    timestamp: datetime
    actor: str
    origin_stage: str
    target_stage_or_route: str
    reason: str


def evaluate_scope_route(session: Session, command: ScopeRouteCommand) -> ProcessHistoryEntry | None:
    execution = session.get(ImpactExecution, command.impact_execution_id)
    if execution is None or execution.execution_status != "Completed" or execution.routing_status != "Completed":
        raise ValueError("scope routing requires a completed and routed execution")
    if session.get(ProcessHistoryEntry, command.process_history_id) is not None:
        raise ValueError("Process-history Entry already exists")
    revision_keys = set(session.execute(select(
        OverlayChangeItemMembership.change_item_id,
        OverlayChangeItemMembership.change_item_revision,
    ).where(OverlayChangeItemMembership.overlay_revision_id == execution.overlay_revision_id)))
    revisions = [session.get(ChangeItemRevision, key) for key in revision_keys]
    applicability_targets = {r.target_id for r in revisions if r is not None and r.action == "Change Applicability"}

    for candidate in session.scalars(select(ImpactCandidate).where(
        ImpactCandidate.impact_execution_id == execution.impact_execution_id,
        ImpactCandidate.candidate_type == "Product Structure Occurrence",
        ImpactCandidate.affected_domain == "Product Engineering",
    ).order_by(ImpactCandidate.impact_candidate_id)):
        assessments = list(session.scalars(select(Assessment).join(
            AssessmentImpactLink, AssessmentImpactLink.assessment_id == Assessment.assessment_id
        ).where(AssessmentImpactLink.impact_candidate_id == candidate.impact_candidate_id)))
        assessment = assessments[0] if len(assessments) == 1 else None
        conclusion = None if assessment is None else session.scalar(select(
            AssessmentRequirementConclusion.conclusion).where(
                AssessmentRequirementConclusion.assessment_id == assessment.assessment_id,
                AssessmentRequirementConclusion.requirement_id == "REQ-004"))
        occurrence_member = session.scalar(select(BaselineMember).where(
            BaselineMember.assessment_baseline_id == execution.assessment_baseline_id,
            BaselineMember.object_type == "Product Structure Occurrence",
            BaselineMember.object_id == candidate.candidate_reference))
        proposed_product = session.scalar(select(OverlayLocalObject).where(
            OverlayLocalObject.overlay_revision_id == execution.overlay_revision_id,
            OverlayLocalObject.object_type == "Product Version"))
        relation = "Not Determinable"
        if occurrence_member is not None and proposed_product is not None:
            relation = validated_scope_relation(
                proposed_product.state_payload.get("validated_configuration_scope", ""),
                occurrence_member.snapshot_payload.get("applicability_rule", {}).get("expression", ""),
            )
        provenance_sources = frozenset(session.execute(select(
            ImpactCandidateProvenance.change_item_id,
            ImpactCandidateProvenance.change_item_revision,
        ).where(ImpactCandidateProvenance.impact_candidate_id == candidate.impact_candidate_id)))
        spec = evaluate_rrr05(Rrr05Input(
            validated_scope_relation=relation,
            product_engineering_assessment_complete=assessment is not None and assessment.domain == "Product Engineering" and assessment.assessment_state == "Complete",
            assessment_linked_to_occurrence_candidate=assessment is not None,
            req_004_conclusion=conclusion,
            overlay_contains_matching_applicability_change=candidate.candidate_reference in applicability_targets,
        ), provenance_sources)
        if spec is not None:
            entry = ProcessHistoryEntry(process_history_id=command.process_history_id,
                change_case_id=execution.change_case_id, entry_type="Scope Revision Required",
                timestamp=command.timestamp, actor=command.actor, origin_stage=command.origin_stage,
                target_stage_or_route=command.target_stage_or_route, reason=command.reason,
                affected_change_item_id=spec.affected_change_item_id,
                affected_change_item_revision=spec.affected_change_item_revision)
            session.add(entry); session.flush()
            return entry
    return None
