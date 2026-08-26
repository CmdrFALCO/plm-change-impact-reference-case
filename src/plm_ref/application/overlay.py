from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from plm_ref.application.change_case import active_proposed_change_scope
from plm_ref.domain.errors import OverlayExecutionEligibilityError
from plm_ref.domain.payloads import (
    BaselineOccurrenceSnapshot,
    BaselineProductVersionSnapshot,
    ChangeApplicabilityCurrentReference,
    ChangeApplicabilityProposalPayload,
    OverlayOccurrenceStatePayload,
    OverlayProductVersionStatePayload,
    ReviseProductStateCurrentReference,
    ReviseProductStateProposalPayload,
)
from plm_ref.infrastructure.db.models import (
    AssessmentBaseline,
    BaselineMember,
    ChangeItemRevision,
    OverlayChangeItemMembership,
    OverlayLocalObject,
    OverlayRevision,
    ProductVersion,
)


class _StrictCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OverlayRevisionInput(_StrictCommand):
    overlay_revision_id: str
    change_case_id: str
    created_at: datetime


class OverlayChangeItemMembershipInput(_StrictCommand):
    overlay_revision_id: str
    change_item_id: str
    change_item_revision: str


class OverlayLocalObjectIdentityInput(_StrictCommand):
    overlay_local_object_id: str
    source_change_item_id: str
    source_change_item_revision: str


class CandidateOverlayRevision(_StrictCommand):
    revision: OverlayRevisionInput
    memberships: tuple[OverlayChangeItemMembershipInput, ...]
    local_object_identities: tuple[OverlayLocalObjectIdentityInput, ...]


@dataclass(frozen=True)
class OverlayExecutionEligibilityResult:
    status: Literal["Pass", "Fail"]
    assessment_baseline_id: str
    active_change_items: tuple[str, ...]
    reasons: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return self.status == "Pass"


def _item_key(change_item_id: str, change_item_revision: str) -> str:
    return f"{change_item_id}:{change_item_revision}"


def _default_overlay_object_ids(
    session: Session,
    overlay_revision_id: str,
    memberships: Sequence[OverlayChangeItemMembershipInput],
) -> dict[str, str]:
    stem = (
        overlay_revision_id[3:]
        if overlay_revision_id.startswith("OV-")
        else overlay_revision_id
    )
    suffix_by_item: dict[str, str] = {}
    suffix_counts: Counter[str] = Counter()
    for membership in memberships:
        item = session.get(
            ChangeItemRevision,
            (membership.change_item_id, membership.change_item_revision),
        )
        suffix = {
            "Revise Product State": "PV",
            "Change Applicability": "PSO",
        }.get(item.action if item is not None else "", membership.change_item_id)
        suffix_by_item[membership.change_item_id] = suffix
        suffix_counts[suffix] += 1

    result: dict[str, str] = {}
    for membership in memberships:
        suffix = suffix_by_item[membership.change_item_id]
        if suffix_counts[suffix] == 1:
            result[membership.change_item_id] = f"OVOBJ-{stem}-{suffix}"
        else:
            result[membership.change_item_id] = (
                f"OVOBJ-{stem}-{suffix}-{membership.change_item_id}"
            )
    return result


def construct_candidate_overlay(
    session: Session,
    revision: OverlayRevisionInput,
    memberships: Sequence[OverlayChangeItemMembershipInput] | None = None,
    local_object_ids: Mapping[str, str] | None = None,
) -> CandidateOverlayRevision:
    """Construct a candidate without persisting any overlay state.

    Omitting memberships captures the exact currently Active selected revision set.
    Supplying memberships permits validation of an externally prepared candidate.
    """

    if memberships is None:
        memberships = [
            OverlayChangeItemMembershipInput(
                overlay_revision_id=revision.overlay_revision_id,
                change_item_id=item.change_item_id,
                change_item_revision=item.change_item_revision,
            )
            for item in active_proposed_change_scope(session, revision.change_case_id)
        ]
    else:
        memberships = list(memberships)

    object_ids = (
        dict(local_object_ids)
        if local_object_ids is not None
        else _default_overlay_object_ids(
            session, revision.overlay_revision_id, memberships
        )
    )
    identities = tuple(
        OverlayLocalObjectIdentityInput(
            overlay_local_object_id=object_ids[membership.change_item_id],
            source_change_item_id=membership.change_item_id,
            source_change_item_revision=membership.change_item_revision,
        )
        for membership in memberships
        if membership.change_item_id in object_ids
    )
    return CandidateOverlayRevision(
        revision=revision,
        memberships=tuple(memberships),
        local_object_identities=identities,
    )


def _membership_reasons(
    session: Session, candidate: CandidateOverlayRevision
) -> tuple[list[str], list[ChangeItemRevision]]:
    reasons: list[str] = []
    overlay = candidate.revision
    active = active_proposed_change_scope(session, overlay.change_case_id)
    expected = {
        (item.change_item_id, item.change_item_revision) for item in active
    }
    actual_pairs = [
        (membership.change_item_id, membership.change_item_revision)
        for membership in candidate.memberships
    ]
    actual = set(actual_pairs)

    if not candidate.memberships:
        reasons.append("Overlay Revision must contain at least one Change Item revision")
    duplicate_identities = sorted(
        item_id
        for item_id, count in Counter(item_id for item_id, _ in actual_pairs).items()
        if count > 1
    )
    if duplicate_identities:
        reasons.append(
            "Overlay contains duplicate Change Item identity: "
            + ", ".join(duplicate_identities)
        )
    if actual != expected or len(actual_pairs) != len(expected):
        reasons.append(
            "Overlay membership does not exactly match the Active selected proposal revisions"
        )
    if any(
        membership.overlay_revision_id != overlay.overlay_revision_id
        for membership in candidate.memberships
    ):
        reasons.append("Overlay membership references another Overlay Revision")

    revisions: list[ChangeItemRevision] = []
    for membership in candidate.memberships:
        item = session.get(
            ChangeItemRevision,
            (membership.change_item_id, membership.change_item_revision),
        )
        if item is None:
            reasons.append(
                f"{_item_key(membership.change_item_id, membership.change_item_revision)} "
                "does not exist"
            )
            continue
        if item.change_case_id != overlay.change_case_id:
            reasons.append(
                f"{_item_key(item.change_item_id, item.change_item_revision)} belongs "
                "to another Change Case"
            )
        revisions.append(item)

    identity_pairs = [
        (identity.source_change_item_id, identity.source_change_item_revision)
        for identity in candidate.local_object_identities
    ]
    if set(identity_pairs) != actual or len(identity_pairs) != len(actual_pairs):
        reasons.append(
            "Overlay-local object identities do not exactly cover Overlay membership"
        )
    object_ids = [
        identity.overlay_local_object_id
        for identity in candidate.local_object_identities
    ]
    if len(object_ids) != len(set(object_ids)):
        reasons.append("Overlay-local object identity is not unique within the Overlay Revision")

    return reasons, revisions


def _baseline_members_by_identity(
    session: Session, assessment_baseline_id: str
) -> dict[tuple[str, str], BaselineMember]:
    members = session.scalars(
        select(BaselineMember).where(
            BaselineMember.assessment_baseline_id == assessment_baseline_id
        )
    )
    return {(member.object_type, member.object_id): member for member in members}


def evaluate_overlay_execution_eligibility(
    session: Session,
    assessment_baseline_id: str,
    candidate: CandidateOverlayRevision,
) -> OverlayExecutionEligibilityResult:
    """Evaluate the frozen post-Gate-A, baseline-relative overlay rules."""

    reasons, revisions = _membership_reasons(session, candidate)
    baseline = session.get(AssessmentBaseline, assessment_baseline_id)
    if baseline is None:
        reasons.append(f"Assessment Baseline {assessment_baseline_id} does not exist")
        baseline_members: dict[tuple[str, str], BaselineMember] = {}
    else:
        if baseline.change_case_id != candidate.revision.change_case_id:
            reasons.append("Assessment Baseline belongs to another Change Case")
        baseline_members = _baseline_members_by_identity(
            session, assessment_baseline_id
        )

    proposed_successors: defaultdict[tuple[str, str, str], list[str]] = defaultdict(list)
    for item in revisions:
        key = _item_key(item.change_item_id, item.change_item_revision)
        if item.action == "Revise Product State":
            member = baseline_members.get(("Product Version", item.target_id))
            if member is None:
                reasons.append(f"{key} target Product Version is absent from the baseline")
            else:
                try:
                    current = ReviseProductStateCurrentReference.model_validate(
                        item.current_state_reference
                    )
                    captured = BaselineProductVersionSnapshot.model_validate(
                        member.snapshot_payload
                    )
                except ValidationError:
                    reasons.append(
                        f"{key} baseline/current Product Version state is malformed"
                    )
                else:
                    if (
                        current.product_version_id != item.target_id
                        or captured.product_version_id != item.target_id
                        or current.product_version_id != captured.product_version_id
                        or current.revision != captured.revision
                        or current.iteration != captured.iteration
                    ):
                        reasons.append(
                            f"{key} baseline Product Version state does not match "
                            "current_state_reference"
                        )

            try:
                proposed = ReviseProductStateProposalPayload.model_validate(
                    item.proposed_state_payload
                )
            except ValidationError:
                reasons.append(f"{key} proposed Product Version state is malformed")
                continue
            successor = (
                proposed.product_element_id,
                proposed.proposed_revision,
                proposed.proposed_iteration,
            )
            proposed_successors[successor].append(key)
            authoritative_collision = session.scalar(
                select(ProductVersion.product_version_id)
                .where(
                    ProductVersion.product_element_id == successor[0],
                    ProductVersion.revision == successor[1],
                    ProductVersion.iteration == successor[2],
                )
                .limit(1)
            )
            if authoritative_collision is not None:
                reasons.append(
                    f"{key} proposed successor identity collides with authoritative "
                    f"Product Version {authoritative_collision}"
                )

        elif item.action == "Change Applicability":
            member = baseline_members.get(
                ("Product Structure Occurrence", item.target_id)
            )
            if member is None:
                reasons.append(
                    f"{key} target Product Structure Occurrence is absent from the baseline"
                )
            else:
                try:
                    current = ChangeApplicabilityCurrentReference.model_validate(
                        item.current_state_reference
                    )
                    captured = BaselineOccurrenceSnapshot.model_validate(
                        member.snapshot_payload
                    )
                except ValidationError:
                    reasons.append(
                        f"{key} baseline/current occurrence state is malformed"
                    )
                else:
                    if (
                        current.occurrence_id != item.target_id
                        or captured.occurrence_id != item.target_id
                    ):
                        reasons.append(
                            f"{key} baseline occurrence state does not match "
                            "current_state_reference"
                        )
                    if (
                        current.applicability_rule_id
                        != captured.applicability_rule.rule_id
                        or current.applicability_rule_version
                        != captured.applicability_rule.rule_version
                    ):
                        reasons.append(
                            f"{key} predecessor Applicability Rule does not match the "
                            "captured baseline occurrence"
                        )
            try:
                ChangeApplicabilityProposalPayload.model_validate(
                    item.proposed_state_payload
                )
            except ValidationError:
                reasons.append(f"{key} proposed Applicability Rule state is malformed")
        else:
            reasons.append(f"{key} uses an unsupported action")

    for successor, sources in proposed_successors.items():
        if len(sources) > 1:
            reasons.append(
                "Proposed successor identity "
                f"{successor[0]}:{successor[1]}.{successor[2]} collides within "
                "the Overlay Revision"
            )

    active_items = tuple(
        _item_key(item.change_item_id, item.change_item_revision)
        for item in active_proposed_change_scope(
            session, candidate.revision.change_case_id
        )
    )
    return OverlayExecutionEligibilityResult(
        status="Pass" if not reasons else "Fail",
        assessment_baseline_id=assessment_baseline_id,
        active_change_items=active_items,
        reasons=tuple(reasons),
    )


def _materialized_objects(
    session: Session,
    assessment_baseline_id: str,
    candidate: CandidateOverlayRevision,
) -> list[OverlayLocalObject]:
    identity_by_source = {
        (
            identity.source_change_item_id,
            identity.source_change_item_revision,
        ): identity.overlay_local_object_id
        for identity in candidate.local_object_identities
    }
    baseline_members = _baseline_members_by_identity(
        session, assessment_baseline_id
    )
    product_objects: list[OverlayLocalObject] = []
    occurrence_items: list[ChangeItemRevision] = []

    for membership in candidate.memberships:
        item = session.get(
            ChangeItemRevision,
            (membership.change_item_id, membership.change_item_revision),
        )
        assert item is not None  # eligibility already verified the exact revision set
        if item.action == "Revise Product State":
            state = OverlayProductVersionStatePayload.model_validate(
                item.proposed_state_payload
            ).model_dump(mode="json")
            product_objects.append(
                OverlayLocalObject(
                    overlay_revision_id=candidate.revision.overlay_revision_id,
                    overlay_local_object_id=identity_by_source[
                        (item.change_item_id, item.change_item_revision)
                    ],
                    object_type="Product Version",
                    source_change_item_id=item.change_item_id,
                    source_change_item_revision=item.change_item_revision,
                    state_payload=state,
                )
            )
        else:
            occurrence_items.append(item)

    proposed_successor_by_predecessor = {
        obj.state_payload["supersedes_product_version_id"]: obj.overlay_local_object_id
        for obj in product_objects
    }
    occurrence_objects: list[OverlayLocalObject] = []
    for item in occurrence_items:
        captured = BaselineOccurrenceSnapshot.model_validate(
            baseline_members[
                ("Product Structure Occurrence", item.target_id)
            ].snapshot_payload
        )
        proposed = ChangeApplicabilityProposalPayload.model_validate(
            item.proposed_state_payload
        )
        state = OverlayOccurrenceStatePayload(
            occurrence_id=captured.occurrence_id,
            parent_product_version_id=captured.parent_product_version_id,
            child_product_version_reference=proposed_successor_by_predecessor.get(
                captured.child_product_version_id,
                captured.child_product_version_id,
            ),
            position=captured.position,
            quantity=captured.quantity,
            unit=captured.unit,
            applicability_rule=proposed.applicability_rule,
            effectivity_specification=captured.effectivity_specification,
        ).model_dump(mode="json")
        occurrence_objects.append(
            OverlayLocalObject(
                overlay_revision_id=candidate.revision.overlay_revision_id,
                overlay_local_object_id=identity_by_source[
                    (item.change_item_id, item.change_item_revision)
                ],
                object_type="Product Structure Occurrence",
                source_change_item_id=item.change_item_id,
                source_change_item_revision=item.change_item_revision,
                state_payload=state,
            )
        )
    return [*product_objects, *occurrence_objects]


def materialize_overlay_revision(
    session: Session,
    assessment_baseline_id: str,
    candidate: CandidateOverlayRevision,
) -> OverlayRevision:
    """Validate and atomically stage an Overlay Revision and all of its children."""

    overlay_id = candidate.revision.overlay_revision_id
    if session.get(OverlayRevision, overlay_id) is not None:
        raise ValueError(f"Overlay Revision {overlay_id} already exists")
    eligibility = evaluate_overlay_execution_eligibility(
        session, assessment_baseline_id, candidate
    )
    if not eligibility.passed:
        raise OverlayExecutionEligibilityError(eligibility.reasons)

    record = OverlayRevision(**candidate.revision.model_dump())
    memberships = [
        OverlayChangeItemMembership(**membership.model_dump())
        for membership in candidate.memberships
    ]
    objects = _materialized_objects(
        session, assessment_baseline_id, candidate
    )
    session.add(record)
    session.flush()
    session.add_all(memberships)
    session.flush()
    session.add_all(objects)
    session.flush()
    return record


def create_overlay_revision(
    session: Session,
    assessment_baseline_id: str,
    revision: OverlayRevisionInput,
    memberships: Sequence[OverlayChangeItemMembershipInput] | None = None,
    local_object_ids: Mapping[str, str] | None = None,
) -> OverlayRevision:
    candidate = construct_candidate_overlay(
        session,
        revision,
        memberships=memberships,
        local_object_ids=local_object_ids,
    )
    return materialize_overlay_revision(
        session, assessment_baseline_id, candidate
    )
