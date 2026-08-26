from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from plm_ref.application.change_case import active_proposed_change_scope
from plm_ref.domain.errors import (
    ImpactExecutionLineageError,
    ImpactResultValidationError,
)
from plm_ref.infrastructure.db.models import (
    AssessmentBaseline,
    BaselineMember,
    ChangeCase,
    ChangeItemRevision,
    ImpactCandidate,
    ImpactCandidatePathStep,
    ImpactCandidateProvenance,
    ImpactExecution,
    OverlayChangeItemMembership,
    OverlayLocalObject,
    OverlayRevision,
)
from plm_ref.infrastructure.impact.port import (
    ChangeItemRevisionReference,
    ImpactAnalysisPort,
    ImpactCandidateSpec,
    ImpactExecutionContext,
)


class ImpactExecutionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    impact_execution_id: str
    change_case_id: str
    assessment_baseline_id: str
    overlay_revision_id: str
    rule_set_version: Literal["RRR-v0.1"]
    execution_timestamp: datetime


def _item_key(change_item_id: str, change_item_revision: str) -> tuple[str, str]:
    return change_item_id, change_item_revision


def validate_execution_lineage(
    session: Session, command: ImpactExecutionInput
) -> ImpactExecutionContext:
    """Resolve and validate the complete case-local execution lineage."""

    reasons: list[str] = []
    if session.get(ImpactExecution, command.impact_execution_id) is not None:
        reasons.append(
            f"Impact-analysis Execution {command.impact_execution_id} already exists"
        )

    change_case = session.get(ChangeCase, command.change_case_id)
    if change_case is None:
        reasons.append(f"Change Case {command.change_case_id} does not exist")

    baseline = session.get(AssessmentBaseline, command.assessment_baseline_id)
    if baseline is None:
        reasons.append(
            f"Assessment Baseline {command.assessment_baseline_id} does not exist"
        )
    else:
        if baseline.change_case_id != command.change_case_id:
            reasons.append("Assessment Baseline belongs to another Change Case")
        if baseline.rule_set_version != command.rule_set_version:
            reasons.append("Assessment Baseline uses another rule-set version")

    overlay = session.get(OverlayRevision, command.overlay_revision_id)
    if overlay is None:
        reasons.append(f"Overlay Revision {command.overlay_revision_id} does not exist")
    elif overlay.change_case_id != command.change_case_id:
        reasons.append("Overlay Revision belongs to another Change Case")

    memberships = list(
        session.scalars(
            select(OverlayChangeItemMembership)
            .where(
                OverlayChangeItemMembership.overlay_revision_id
                == command.overlay_revision_id
            )
            .order_by(
                OverlayChangeItemMembership.change_item_id,
                OverlayChangeItemMembership.change_item_revision,
            )
        )
    )
    membership_keys = [
        _item_key(item.change_item_id, item.change_item_revision)
        for item in memberships
    ]
    if not membership_keys:
        reasons.append("Overlay Revision has no Change Item revision membership")

    if change_case is not None:
        active_keys = {
            _item_key(item.change_item_id, item.change_item_revision)
            for item in active_proposed_change_scope(session, command.change_case_id)
        }
        if set(membership_keys) != active_keys or len(membership_keys) != len(
            active_keys
        ):
            reasons.append(
                "Overlay membership does not exactly match the Active selected "
                "Change Item revisions"
            )

    for change_item_id, change_item_revision in membership_keys:
        revision = session.get(
            ChangeItemRevision, (change_item_id, change_item_revision)
        )
        if revision is None:
            reasons.append(
                f"Change Item Revision {change_item_id}:{change_item_revision} "
                "does not exist"
            )
        elif revision.change_case_id != command.change_case_id:
            reasons.append(
                f"Change Item Revision {change_item_id}:{change_item_revision} "
                "belongs to another Change Case"
            )

    local_objects = list(
        session.scalars(
            select(OverlayLocalObject)
            .where(
                OverlayLocalObject.overlay_revision_id
                == command.overlay_revision_id
            )
            .order_by(OverlayLocalObject.overlay_local_object_id)
        )
    )
    local_sources = [
        _item_key(obj.source_change_item_id, obj.source_change_item_revision)
        for obj in local_objects
    ]
    if (
        set(local_sources) != set(membership_keys)
        or len(local_sources) != len(membership_keys)
    ):
        reasons.append(
            "Overlay-local Objects do not exactly cover Overlay membership"
        )

    if reasons:
        raise ImpactExecutionLineageError("; ".join(reasons))

    return ImpactExecutionContext(
        impact_execution_id=command.impact_execution_id,
        change_case_id=command.change_case_id,
        assessment_baseline_id=command.assessment_baseline_id,
        overlay_revision_id=command.overlay_revision_id,
        rule_set_version=command.rule_set_version,
        overlay_membership=tuple(
            ChangeItemRevisionReference(
                change_item_id=item.change_item_id,
                change_item_revision=item.change_item_revision,
            )
            for item in memberships
        ),
        overlay_local_object_ids=tuple(
            obj.overlay_local_object_id for obj in local_objects
        ),
    )


def _validate_adapter_output(
    session: Session,
    context: ImpactExecutionContext,
    raw_candidates: Sequence[ImpactCandidateSpec] | object,
) -> tuple[ImpactCandidateSpec, ...]:
    try:
        if isinstance(raw_candidates, (str, bytes)):
            raise TypeError("candidate output must be a sequence")
        candidates = tuple(
            ImpactCandidateSpec.model_validate(candidate)
            for candidate in raw_candidates  # type: ignore[union-attr]
        )
    except (TypeError, ValidationError) as exc:
        raise ImpactResultValidationError(
            "adapter output does not match the bounded impact result schema"
        ) from exc

    candidate_ids = [item.impact_candidate_id for item in candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ImpactResultValidationError("Impact Candidate IDs are not unique")
    if candidate_ids:
        existing_candidate = session.scalar(
            select(ImpactCandidate.impact_candidate_id)
            .where(ImpactCandidate.impact_candidate_id.in_(candidate_ids))
            .limit(1)
        )
        if existing_candidate is not None:
            raise ImpactResultValidationError(
                f"Impact Candidate {existing_candidate} belongs to another execution"
            )

    membership = {
        _item_key(item.change_item_id, item.change_item_revision)
        for item in context.overlay_membership
    }
    baseline_references = set(
        session.scalars(
            select(BaselineMember.baseline_member_id).where(
                BaselineMember.assessment_baseline_id
                == context.assessment_baseline_id
            )
        )
    )
    proposed_references = set(context.overlay_local_object_ids)
    provenance_ids: list[str] = []

    for candidate in candidates:
        for provenance in candidate.provenance:
            provenance_ids.append(provenance.impact_candidate_provenance_id)
            change_item_key = _item_key(
                provenance.change_item_id, provenance.change_item_revision
            )
            if change_item_key not in membership:
                raise ImpactResultValidationError(
                    "provenance Change Item revision is outside execution Overlay "
                    "membership"
                )

            steps = provenance.dependency_path
            sequences = [step.sequence for step in steps]
            if sequences != list(range(1, len(steps) + 1)):
                raise ImpactResultValidationError(
                    "provenance path sequence must start at 1 and be contiguous"
                )
            for previous, following in zip(steps, steps[1:]):
                if previous.target_reference != following.source_reference:
                    raise ImpactResultValidationError(
                        "adjacent provenance path steps are not connected"
                    )
            for step in steps:
                allowed_references = (
                    baseline_references
                    if step.state_context == "Current State"
                    else proposed_references
                )
                if (
                    step.source_reference not in allowed_references
                    or step.target_reference not in allowed_references
                ):
                    raise ImpactResultValidationError(
                        f"{step.state_context} provenance references state outside "
                        "the execution lineage"
                    )

    if len(provenance_ids) != len(set(provenance_ids)):
        raise ImpactResultValidationError("provenance IDs are not unique")
    if provenance_ids:
        existing_provenance = session.scalar(
            select(ImpactCandidateProvenance.impact_candidate_provenance_id)
            .where(
                ImpactCandidateProvenance.impact_candidate_provenance_id.in_(
                    provenance_ids
                )
            )
            .limit(1)
        )
        if existing_provenance is not None:
            raise ImpactResultValidationError(
                f"provenance {existing_provenance} belongs to another execution"
            )
    return candidates


def _persist_results(
    session: Session,
    impact_execution_id: str,
    candidates: tuple[ImpactCandidateSpec, ...],
) -> None:
    session.add_all(
        ImpactCandidate(
            impact_candidate_id=candidate.impact_candidate_id,
            impact_execution_id=impact_execution_id,
            candidate_type=candidate.candidate_type,
            candidate_reference=candidate.candidate_reference,
            affected_domain=candidate.affected_domain,
            candidate_state="New",
        )
        for candidate in candidates
    )
    session.flush()

    provenance_records = []
    path_steps = []
    for candidate in candidates:
        for provenance in candidate.provenance:
            provenance_records.append(
                ImpactCandidateProvenance(
                    impact_candidate_provenance_id=(
                        provenance.impact_candidate_provenance_id
                    ),
                    impact_candidate_id=candidate.impact_candidate_id,
                    change_item_id=provenance.change_item_id,
                    change_item_revision=provenance.change_item_revision,
                )
            )
            path_steps.extend(
                ImpactCandidatePathStep(
                    impact_candidate_provenance_id=(
                        provenance.impact_candidate_provenance_id
                    ),
                    **step.model_dump(),
                )
                for step in provenance.dependency_path
            )
    session.add_all(provenance_records)
    session.flush()
    session.add_all(path_steps)
    session.flush()


def execute_impact_analysis(
    session: Session,
    command: ImpactExecutionInput,
    adapter: ImpactAnalysisPort,
) -> ImpactExecution:
    """Execute INC-05 discovery, persisting either a complete result or failure."""

    context = validate_execution_lineage(session, command)
    execution = ImpactExecution(
        **command.model_dump(),
        execution_status="Running",
        routing_status="Not Started",
    )
    session.add(execution)
    session.flush()

    try:
        raw_candidates = adapter.run(context)
        candidates = _validate_adapter_output(session, context, raw_candidates)
        with session.begin_nested():
            _persist_results(session, command.impact_execution_id, candidates)
            execution.execution_status = "Completed"
            execution.routing_status = "Not Started"
            session.flush()
    except Exception:
        execution.execution_status = "Failed"
        execution.routing_status = "Not Started"
        session.flush()
    return execution
