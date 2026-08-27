from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from typing import TypeVar

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from plm_ref.domain.errors import RoutingEligibilityError, RoutingInputError
from plm_ref.domain.payloads import (
    BaselineOccurrenceSnapshot,
    BaselineProductVersionSnapshot,
    BaselineRequirementSnapshot,
    OverlayOccurrenceStatePayload,
    OverlayProductVersionStatePayload,
)
from plm_ref.infrastructure.db.models import (
    AssessmentBaseline,
    AssessmentObligation,
    BaselineMember,
    ChangeCase,
    ChangeItemRevision,
    ImpactCandidate,
    ImpactExecution,
    OverlayChangeItemMembership,
    OverlayLocalObject,
    OverlayRevision,
)
from plm_ref.rules.rrr_v01 import (
    RULE_SET_REGISTRY,
    AssessmentObligationSpec,
    CandidateRoutingInput,
    OccurrenceRoutingInput,
    ProductStateRoutingInput,
    RrrV01ExecutionContext,
)

_RecordT = TypeVar("_RecordT")


def _exactly_one(
    records: Sequence[_RecordT], description: str
) -> _RecordT:
    if len(records) != 1:
        raise RoutingInputError(f"expected exactly one {description}")
    return records[0]


def _build_routing_context(
    session: Session, execution: ImpactExecution
) -> RrrV01ExecutionContext:
    change_case = session.get(ChangeCase, execution.change_case_id)
    baseline = session.get(AssessmentBaseline, execution.assessment_baseline_id)
    overlay = session.get(OverlayRevision, execution.overlay_revision_id)
    if change_case is None or baseline is None or overlay is None:
        raise RoutingInputError("execution lineage is incomplete")
    if (
        baseline.change_case_id != execution.change_case_id
        or overlay.change_case_id != execution.change_case_id
    ):
        raise RoutingInputError("execution baseline/overlay lineage crosses Change Cases")
    if baseline.rule_set_version != execution.rule_set_version:
        raise RoutingInputError("execution and baseline rule-set versions differ")

    memberships = list(
        session.scalars(
            select(OverlayChangeItemMembership)
            .where(
                OverlayChangeItemMembership.overlay_revision_id
                == execution.overlay_revision_id
            )
            .order_by(
                OverlayChangeItemMembership.change_item_id,
                OverlayChangeItemMembership.change_item_revision,
            )
        )
    )
    if not memberships:
        raise RoutingInputError("execution Overlay Revision has no membership")
    membership_keys = {
        (item.change_item_id, item.change_item_revision) for item in memberships
    }
    if len(membership_keys) != len(memberships):
        raise RoutingInputError("execution Overlay membership is not exact")

    revisions: dict[tuple[str, str], ChangeItemRevision] = {}
    for key in membership_keys:
        revision = session.get(ChangeItemRevision, key)
        if revision is None or revision.change_case_id != execution.change_case_id:
            raise RoutingInputError(
                f"Overlay Change Item Revision {key[0]}:{key[1]} is not case-local"
            )
        revisions[key] = revision

    local_objects = list(
        session.scalars(
            select(OverlayLocalObject)
            .where(
                OverlayLocalObject.overlay_revision_id
                == execution.overlay_revision_id
            )
            .order_by(OverlayLocalObject.overlay_local_object_id)
        )
    )
    local_by_source: defaultdict[
        tuple[str, str], list[OverlayLocalObject]
    ] = defaultdict(list)
    for local_object in local_objects:
        local_by_source[
            (
                local_object.source_change_item_id,
                local_object.source_change_item_revision,
            )
        ].append(local_object)
    if set(local_by_source) != membership_keys or any(
        len(objects) != 1 for objects in local_by_source.values()
    ):
        raise RoutingInputError(
            "Overlay-local Objects do not exactly cover execution membership"
        )

    baseline_members = list(
        session.scalars(
            select(BaselineMember).where(
                BaselineMember.assessment_baseline_id
                == execution.assessment_baseline_id
            )
        )
    )
    baseline_by_identity: defaultdict[
        tuple[str, str], list[BaselineMember]
    ] = defaultdict(list)
    for member in baseline_members:
        baseline_by_identity[(member.object_type, member.object_id)].append(member)

    occurrence_members = tuple(
        member
        for member in baseline_members
        if member.object_type == "Product Structure Occurrence"
    )
    requirement_members = tuple(
        member for member in baseline_members if member.object_type == "Requirement"
    )
    try:
        captured_occurrences = tuple(
            BaselineOccurrenceSnapshot.model_validate(member.snapshot_payload)
            for member in occurrence_members
        )
        captured_requirements = tuple(
            BaselineRequirementSnapshot.model_validate(member.snapshot_payload)
            for member in requirement_members
        )
    except ValidationError as exc:
        raise RoutingInputError("execution Baseline Member payload is malformed") from exc
    if any(
        occurrence.occurrence_id != member.object_id
        for member, occurrence in zip(occurrence_members, captured_occurrences)
    ):
        raise RoutingInputError("captured occurrence identity is inconsistent")
    if any(
        requirement.requirement_id != member.object_id
        for member, requirement in zip(
            requirement_members, captured_requirements
        )
    ):
        raise RoutingInputError("captured Requirement identity is inconsistent")
    baseline_requirement_ids = frozenset(
        requirement.requirement_id for requirement in captured_requirements
    )

    applicability_targets: set[str] = set()
    for key, revision in revisions.items():
        local_object = _exactly_one(
            local_by_source[key], "Overlay-local Object per Change Item revision"
        )
        if revision.action == "Change Applicability":
            if revision.target_type != "Product Structure Occurrence":
                raise RoutingInputError("Change Applicability target type is malformed")
            try:
                state = OverlayOccurrenceStatePayload.model_validate(
                    local_object.state_payload
                )
            except ValidationError as exc:
                raise RoutingInputError(
                    "Overlay-local occurrence state is malformed"
                ) from exc
            if (
                local_object.object_type != "Product Structure Occurrence"
                or state.occurrence_id != revision.target_id
            ):
                raise RoutingInputError(
                    "Overlay-local occurrence does not match its Change Item target"
                )
            applicability_targets.add(revision.target_id)
        elif revision.action != "Revise Product State":
            raise RoutingInputError(
                f"unsupported Change Item action {revision.action}"
            )

    product_states: list[ProductStateRoutingInput] = []
    for key, revision in revisions.items():
        if revision.action != "Revise Product State":
            continue
        if revision.target_type != "Product Version":
            raise RoutingInputError("Revise Product State target type is malformed")
        baseline_product_member = _exactly_one(
            baseline_by_identity[("Product Version", revision.target_id)],
            f"captured Product Version {revision.target_id}",
        )
        local_object = _exactly_one(
            local_by_source[key], "Overlay-local Product Version"
        )
        try:
            predecessor = BaselineProductVersionSnapshot.model_validate(
                baseline_product_member.snapshot_payload
            )
            proposed = OverlayProductVersionStatePayload.model_validate(
                local_object.state_payload
            )
        except ValidationError as exc:
            raise RoutingInputError(
                "captured or proposed Product Version state is malformed"
            ) from exc
        if (
            predecessor.product_version_id != revision.target_id
            or proposed.supersedes_product_version_id != revision.target_id
            or local_object.object_type != "Product Version"
        ):
            raise RoutingInputError(
                "Product Version routing lineage is internally inconsistent"
            )
        if (
            predecessor.material_characteristic is None
            or predecessor.validated_configuration_scope is None
        ):
            raise RoutingInputError(
                "captured Product Version lacks bounded technical-state inputs"
            )

        affected_occurrences = tuple(
            OccurrenceRoutingInput(
                occurrence_id=occurrence.occurrence_id,
                current_applicability_expression=(
                    occurrence.applicability_rule.expression
                ),
                overlay_contains_applicability_change=(
                    occurrence.occurrence_id in applicability_targets
                ),
            )
            for occurrence in captured_occurrences
            if occurrence.child_product_version_id == revision.target_id
        )
        product_states.append(
            ProductStateRoutingInput(
                predecessor_material_characteristic=(
                    predecessor.material_characteristic
                ),
                proposed_material_characteristic=proposed.material_characteristic,
                proposed_validated_scope=proposed.validated_configuration_scope,
                affected_occurrences=affected_occurrences,
            )
        )

    candidates = tuple(
        session.scalars(
            select(ImpactCandidate)
            .where(
                ImpactCandidate.impact_execution_id
                == execution.impact_execution_id
            )
            .order_by(ImpactCandidate.impact_candidate_id)
        )
    )
    if any(candidate.candidate_state != "New" for candidate in candidates):
        raise RoutingInputError("execution Impact Candidates are not in New state")
    if session.scalar(
        select(AssessmentObligation.assessment_obligation_id)
        .where(
            AssessmentObligation.impact_execution_id
            == execution.impact_execution_id
        )
        .limit(1)
    ) is not None:
        raise RoutingInputError("execution already has Assessment Obligations")

    return RrrV01ExecutionContext(
        impact_execution_id=execution.impact_execution_id,
        change_case_trigger=change_case.trigger,
        product_states=tuple(product_states),
        candidates=tuple(
            CandidateRoutingInput(
                impact_candidate_id=candidate.impact_candidate_id,
                affected_domain=candidate.affected_domain,
            )
            for candidate in candidates
        ),
        baseline_requirement_ids=baseline_requirement_ids,
    )


def _validate_obligation_specs(
    context: RrrV01ExecutionContext,
    specs: tuple[AssessmentObligationSpec, ...],
) -> None:
    obligation_ids = [spec.assessment_obligation_id for spec in specs]
    if len(obligation_ids) != len(set(obligation_ids)):
        raise RoutingInputError("Assessment Obligation IDs are not unique")
    candidate_ids = {
        candidate.impact_candidate_id for candidate in context.candidates
    }
    for spec in specs:
        if not spec.mandatory:
            raise RoutingInputError("RRR-01..04 produced a non-mandatory obligation")
        if (
            spec.impact_candidate_id is not None
            and spec.impact_candidate_id not in candidate_ids
        ):
            raise RoutingInputError(
                "Assessment Obligation references a candidate from another execution"
            )


def _persist_routing_result(
    session: Session,
    execution: ImpactExecution,
    specs: tuple[AssessmentObligationSpec, ...],
) -> None:
    session.add_all(
        AssessmentObligation(
            assessment_obligation_id=spec.assessment_obligation_id,
            impact_execution_id=execution.impact_execution_id,
            impact_candidate_id=spec.impact_candidate_id,
            domain=spec.domain,
            requirement_id=spec.requirement_id,
            mandatory=spec.mandatory,
            fulfilled_by_assessment_id=None,
            routing_rule_reference=spec.routing_rule_reference,
        )
        for spec in specs
    )
    session.flush()

    referenced_candidate_ids = {
        spec.impact_candidate_id
        for spec in specs
        if spec.impact_candidate_id is not None
    }
    if referenced_candidate_ids:
        candidates = list(
            session.scalars(
                select(ImpactCandidate).where(
                    ImpactCandidate.impact_execution_id
                    == execution.impact_execution_id,
                    ImpactCandidate.impact_candidate_id.in_(
                        referenced_candidate_ids
                    ),
                )
            )
        )
        if {candidate.impact_candidate_id for candidate in candidates} != (
            referenced_candidate_ids
        ):
            raise RoutingInputError(
                "routed Impact Candidate set crosses execution boundaries"
            )
        for candidate in candidates:
            if candidate.candidate_state != "New":
                raise RoutingInputError(
                    "routed Impact Candidate cannot transition from its current state"
                )
            candidate.candidate_state = "Assessment Planned"
    execution.routing_status = "Completed"
    session.flush()


def route_impact_execution(
    session: Session, impact_execution_id: str
) -> ImpactExecution:
    """Atomically evaluate and materialise frozen RRR-01 through RRR-04."""

    execution = session.get(ImpactExecution, impact_execution_id)
    if execution is None:
        raise ValueError(
            f"Impact-analysis Execution {impact_execution_id} does not exist"
        )
    if execution.execution_status != "Completed":
        raise RoutingEligibilityError(
            "routing can start only from a Completed Impact-analysis Execution"
        )
    if execution.routing_status != "Not Started":
        raise RoutingEligibilityError(
            "routing can start only when routing status is Not Started"
        )

    try:
        rule_set = RULE_SET_REGISTRY.get(execution.rule_set_version)
        if rule_set is None:
            raise RoutingInputError(
                f"unknown rule-set version {execution.rule_set_version}"
            )
        context = _build_routing_context(session, execution)
        specs = rule_set.evaluate(context)
        _validate_obligation_specs(context, specs)
        with session.begin_nested():
            _persist_routing_result(session, execution, specs)
    except Exception:
        execution.routing_status = "Failed"
        session.flush()
    return execution
