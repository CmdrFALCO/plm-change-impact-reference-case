"""Frozen INC-11 explicit terminal Decision persistence only."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from plm_ref.application.authority import evaluate_authority
from plm_ref.application.change_case import active_proposed_change_scope
from plm_ref.application.readiness import evaluate_authorisation_eligibility, evaluate_gate_b
from plm_ref.infrastructure.db.models import (
    Assessment, AssessmentObligation, AssessmentReuseClassification, ChangeCase,
    ChangeItemRevision, DecisionCondition, DecisionRecord, DecisionScopeItem,
    DecisionSupportAssessment, ImpactExecution, OpenItem, OverlayChangeItemMembership,
)


@dataclass(frozen=True)
class DecisionScopeInput:
    change_item_id: str
    change_item_revision: str


@dataclass(frozen=True)
class DecisionSupportInput:
    decision_support_assessment_id: str
    assessment_id: str


@dataclass(frozen=True)
class DecisionConditionInput:
    decision_condition_id: str
    text: str
    responsible_downstream_role: str
    required_before_stage: Literal["Pre-implementation", "Pre-release", "Post-implementation monitoring"]
    expected_completion_evidence: str


@dataclass(frozen=True)
class DecisionCommand:
    decision_record_id: str
    change_case_id: str
    assessment_baseline_id: str
    overlay_revision_id: str
    impact_execution_id: str
    outcome: Literal["Authorised for Downstream Processing", "Authorised with Conditions", "Rejected"]
    rationale: str
    decision_authority: str
    decision_timestamp: datetime
    scope_items: tuple[DecisionScopeInput, ...]
    support_assessments: tuple[DecisionSupportInput, ...]
    conditions: tuple[DecisionConditionInput, ...]


def _unresolved_decision_open_item(session: Session, case_id: str) -> bool:
    return session.scalar(select(OpenItem.open_item_id).where(
        OpenItem.change_case_id == case_id, OpenItem.blocking_class == "Blocking",
        OpenItem.required_before_stage == "Decision", OpenItem.status != "Resolved",
    ).limit(1)) is not None


def _validate_scope(session: Session, execution: ImpactExecution, scope: tuple[DecisionScopeInput, ...]) -> set[tuple[str, str]]:
    keys = {(item.change_item_id, item.change_item_revision) for item in scope}
    if not keys or len(keys) != len(scope):
        raise ValueError("Decision Scope must be non-empty and unique")
    overlay = set(session.execute(select(
        OverlayChangeItemMembership.change_item_id, OverlayChangeItemMembership.change_item_revision,
    ).where(OverlayChangeItemMembership.overlay_revision_id == execution.overlay_revision_id)))
    if not keys <= overlay:
        raise ValueError("Decision Scope Item is absent from final Overlay Revision")
    already_disposed = set(session.execute(select(
        DecisionScopeItem.change_item_id, DecisionScopeItem.change_item_revision,
    ).where(
        DecisionScopeItem.change_item_id.in_([key[0] for key in keys]),
    )))
    if keys & already_disposed:
        raise ValueError("Change Item revision already has a terminal Decision disposition")
    for key in keys:
        revision = session.get(ChangeItemRevision, key)
        if revision is None or revision.change_case_id != execution.change_case_id:
            raise ValueError("Decision Scope Item crosses Change Case")
    return keys


def _validate_support(session: Session, execution: ImpactExecution, support: tuple[DecisionSupportInput, ...]) -> None:
    supplied = {item.assessment_id for item in support}
    if len(supplied) != len(support):
        raise ValueError("Decision Support Assessments must be unique")
    mandatory = list(session.scalars(select(AssessmentObligation).where(
        AssessmentObligation.impact_execution_id == execution.impact_execution_id,
        AssessmentObligation.mandatory.is_(True),
    )))
    required = {obligation.fulfilled_by_assessment_id for obligation in mandatory}
    if None in required or supplied != required:
        raise ValueError("Decision Support Assessment set is incomplete")
    for assessment_id in supplied:
        assessment = session.get(Assessment, assessment_id)
        if (assessment is None or assessment.change_case_id != execution.change_case_id
                or assessment.assessment_state != "Complete" or not assessment.is_locked):
            raise ValueError("Decision Support Assessment is incompatible")
        if assessment.origin_impact_execution_id != execution.impact_execution_id:
            retained = session.scalar(select(AssessmentReuseClassification.assessment_reuse_classification_id).where(
                AssessmentReuseClassification.assessment_id == assessment.assessment_id,
                AssessmentReuseClassification.target_impact_execution_id == execution.impact_execution_id,
                AssessmentReuseClassification.classification == "Retained",
            ).limit(1))
            if retained is None:
                raise ValueError("historical Decision Support Assessment is not Retained")


def persist_terminal_decision(session: Session, command: DecisionCommand) -> DecisionRecord:
    """Persist only a caller-selected terminal disposition as one atomic unit."""
    if session.get(DecisionRecord, command.decision_record_id) is not None:
        raise ValueError("Decision Record already exists")
    execution = session.get(ImpactExecution, command.impact_execution_id)
    if execution is None or (execution.change_case_id, execution.assessment_baseline_id, execution.overlay_revision_id) != (
        command.change_case_id, command.assessment_baseline_id, command.overlay_revision_id):
        raise ValueError("Decision lineage is not case-local")
    gate = evaluate_gate_b(session, execution.impact_execution_id)
    eligibility = evaluate_authorisation_eligibility(session, gate)
    authority = evaluate_authority(gate, eligibility)
    if command.outcome != "Rejected":
        if gate.gate_b != "Complete" or eligibility.authorisation_eligibility != "Permitted" or authority.authority_sufficient is not True:
            raise ValueError("authorised Decision prerequisites are not satisfied")
        if _unresolved_decision_open_item(session, command.change_case_id):
            raise ValueError("unresolved Decision-blocking Open Item")
    elif authority.authority_sufficient is not True or not command.rationale:
        raise ValueError("Rejected Decision prerequisites are not satisfied")
    scope = _validate_scope(session, execution, command.scope_items)
    _validate_support(session, execution, command.support_assessments)
    if command.outcome == "Authorised for Downstream Processing" and command.conditions:
        raise ValueError("Authorised for Downstream Processing requires zero Decision Conditions")
    if command.outcome == "Authorised with Conditions" and not command.conditions:
        raise ValueError("Authorised with Conditions requires Decision Conditions")
    if command.outcome == "Rejected" and command.conditions:
        raise ValueError("Rejected requires zero Decision Conditions")
    if len({condition.decision_condition_id for condition in command.conditions}) != len(command.conditions):
        raise ValueError("Decision Conditions must be unique")
    with session.begin_nested():
        record = DecisionRecord(decision_record_id=command.decision_record_id,
            change_case_id=command.change_case_id, assessment_baseline_id=command.assessment_baseline_id,
            overlay_revision_id=command.overlay_revision_id, impact_execution_id=command.impact_execution_id,
            required_authority_level=authority.required_authority_level,
            current_authority_level=authority.current_authority_level, outcome=command.outcome,
            rationale=command.rationale, decision_authority=command.decision_authority,
            decision_timestamp=command.decision_timestamp)
        session.add(record); session.flush()
        for item in command.scope_items:
            session.add(DecisionScopeItem(decision_record_id=record.decision_record_id,
                change_item_id=item.change_item_id, change_item_revision=item.change_item_revision))
        for item in command.support_assessments:
            session.add(DecisionSupportAssessment(
                decision_support_assessment_id=item.decision_support_assessment_id,
                decision_record_id=record.decision_record_id, assessment_id=item.assessment_id))
        for item in command.conditions:
            session.add(DecisionCondition(decision_condition_id=item.decision_condition_id,
                decision_record_id=record.decision_record_id, text=item.text,
                responsible_downstream_role=item.responsible_downstream_role,
                required_before_stage=item.required_before_stage,
                expected_completion_evidence=item.expected_completion_evidence))
        active = {(revision.change_item_id, revision.change_item_revision)
            for revision in active_proposed_change_scope(session, command.change_case_id)}
        prior = set(session.execute(select(DecisionScopeItem.change_item_id, DecisionScopeItem.change_item_revision).join(
            DecisionRecord, DecisionRecord.decision_record_id == DecisionScopeItem.decision_record_id
        ).where(DecisionRecord.change_case_id == command.change_case_id)))
        if active <= prior | scope:
            case = session.get(ChangeCase, command.change_case_id)
            case.case_state = "Closed by Decision"; case.closed_at = command.decision_timestamp
        session.flush()
    return record
