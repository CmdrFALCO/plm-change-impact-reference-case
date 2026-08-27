"""Frozen INC-10 authority comparison and non-terminal escalation."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from plm_ref.application.readiness import (
    NOT_EVALUATED, AuthorisationEligibilityResult, GateBResult,
)
from plm_ref.infrastructure.db.models import (
    ChangeCase, ChangeItemRevision, ImpactExecution, OverlayChangeItemMembership,
    ProcessHistoryEntry,
)


@dataclass(frozen=True)
class AuthorityEvaluationResult:
    impact_execution_id: str
    required_authority_level: Literal["Standard", "Elevated"] | str
    current_authority_level: Literal["Standard"] | str
    authority_sufficient: bool | None
    decision_permitted: bool | None
    escalation_required: bool | None


@dataclass(frozen=True)
class EscalationCommand:
    process_history_id: str
    timestamp: datetime
    actor: str


def evaluate_authority(
    gate_b: GateBResult, eligibility: AuthorisationEligibilityResult,
) -> AuthorityEvaluationResult:
    """Compare only the frozen `Standard < Elevated` ordering."""
    if gate_b.gate_b != "Complete":
        return AuthorityEvaluationResult(gate_b.impact_execution_id, NOT_EVALUATED,
            NOT_EVALUATED, None, None, None)
    current = "Standard"
    if eligibility.authorisation_eligibility != "Permitted":
        return AuthorityEvaluationResult(gate_b.impact_execution_id,
            gate_b.required_authority_level, NOT_EVALUATED, None, None, None)
    authority_sufficient = gate_b.required_authority_level == current
    return AuthorityEvaluationResult(gate_b.impact_execution_id,
        gate_b.required_authority_level, current, authority_sufficient,
        authority_sufficient, not authority_sufficient)


def persist_escalation(
    session: Session, result: AuthorityEvaluationResult, command: EscalationCommand,
) -> ProcessHistoryEntry:
    """Persist exactly one frozen Escalated history entry, never a Decision."""
    if result.escalation_required is not True or result.required_authority_level != "Elevated":
        raise ValueError("authority result does not require the frozen Elevated escalation")
    if session.get(ProcessHistoryEntry, command.process_history_id) is not None:
        raise ValueError("Process-history Entry already exists")
    execution = session.get(ImpactExecution, result.impact_execution_id)
    if execution is None:
        raise ValueError("impact execution does not exist")
    case = session.get(ChangeCase, execution.change_case_id)
    if case is None:
        raise ValueError("impact execution Change Case does not exist")
    memberships = list(session.execute(select(
        OverlayChangeItemMembership.change_item_id,
        OverlayChangeItemMembership.change_item_revision,
    ).where(OverlayChangeItemMembership.overlay_revision_id == execution.overlay_revision_id)))
    affected_id = affected_revision = None
    if len(memberships) == 1:
        affected_id, affected_revision = memberships[0]
        revision = session.get(ChangeItemRevision, (affected_id, affected_revision))
        if revision is None or revision.change_case_id != case.change_case_id:
            raise ValueError("escalation scope is not case-local")
    with session.begin_nested():
        entry = ProcessHistoryEntry(
            process_history_id=command.process_history_id,
            change_case_id=case.change_case_id,
            entry_type="Escalated",
            timestamp=command.timestamp,
            actor=command.actor,
            origin_stage="Authority Check",
            target_stage_or_route="Elevated Authority Route",
            reason="Required authority is Elevated while current authority is Standard.",
            affected_change_item_id=affected_id,
            affected_change_item_revision=affected_revision,
        )
        session.add(entry)
        case.case_state = "Decision Ready"
        session.flush()
    return entry
