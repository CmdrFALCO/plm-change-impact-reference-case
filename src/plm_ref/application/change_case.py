from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from plm_ref.domain.payloads import (
    ChangeApplicabilityCurrentReference,
    ChangeApplicabilityProposalPayload,
    EffectivityPayload,
    ReviseProductStateCurrentReference,
    ReviseProductStateProposalPayload,
)
from plm_ref.infrastructure.db.models import (
    ChangeCase,
    ChangeItem,
    ChangeItemProposalState,
    ChangeItemRevision,
    OpenItem,
)


class _StrictCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ChangeCaseInput(_StrictCommand):
    change_case_id: str
    title: str
    trigger: str
    rationale: str
    change_owner: str
    case_state: str
    process_iteration: int
    created_at: datetime
    closed_at: datetime | None = None


class ChangeItemRevisionInput(_StrictCommand):
    change_item_id: str
    change_item_revision: str = Field(pattern=r"^r[1-9]\d*$")
    change_case_id: str
    action: Literal["Revise Product State", "Change Applicability"]
    target_type: str
    target_id: str
    current_state_reference: dict[str, Any]
    proposed_state_payload: dict[str, Any]
    reason: str
    owner: str
    configuration_context_id: str
    intended_effectivity: dict[str, Any]
    revision_created_at: datetime

    @model_validator(mode="after")
    def validate_action_payloads(self) -> Self:
        if self.action == "Revise Product State":
            current = ReviseProductStateCurrentReference.model_validate(
                self.current_state_reference
            )
            proposed = ReviseProductStateProposalPayload.model_validate(
                self.proposed_state_payload
            )
        else:
            current = ChangeApplicabilityCurrentReference.model_validate(
                self.current_state_reference
            )
            proposed = ChangeApplicabilityProposalPayload.model_validate(
                self.proposed_state_payload
            )
        effectivity = EffectivityPayload.model_validate(self.intended_effectivity)
        self.current_state_reference = current.model_dump(mode="json")
        self.proposed_state_payload = proposed.model_dump(mode="json")
        self.intended_effectivity = effectivity.model_dump(mode="json")
        return self


class ProposalStateInput(_StrictCommand):
    change_item_id: str
    change_case_id: str
    selected_revision: str
    proposal_state: Literal["Active", "Removed from Proposal"]
    state_changed_at: datetime
    state_changed_by: str


class OpenItemInput(_StrictCommand):
    open_item_id: str
    change_case_id: str
    source_type: str
    source_id: str
    item_type: Literal["Information Gap", "Data Defect", "Conflict", "Required Action"]
    description: str
    owner: str
    status: Literal["Open", "In Resolution", "Resolved", "Cancelled"]
    blocking_class: Literal["Blocking", "Non-blocking"]
    required_before_stage: Literal["Initial Distribution", "Assessment Completion", "Decision"]
    resolution_evidence_reference: str | None = None
    created_at: datetime
    closed_at: datetime | None = None


def create_change_case(session: Session, data: ChangeCaseInput) -> ChangeCase:
    record = ChangeCase(**data.model_dump())
    session.add(record)
    session.flush()
    return record


def create_change_item(
    session: Session,
    revision_data: ChangeItemRevisionInput,
    proposal_data: ProposalStateInput,
) -> ChangeItemRevision:
    if (
        revision_data.change_item_id != proposal_data.change_item_id
        or revision_data.change_case_id != proposal_data.change_case_id
        or revision_data.change_item_revision != proposal_data.selected_revision
    ):
        raise ValueError(
            "initial Proposal State must select the Change Item revision being created"
        )
    if session.get(ChangeItem, revision_data.change_item_id) is not None:
        raise ValueError("Change Item identity already exists")

    session.add(
        ChangeItem(
            change_item_id=revision_data.change_item_id,
            change_case_id=revision_data.change_case_id,
        )
    )
    session.flush()
    revision = _insert_change_item_revision(session, revision_data)
    session.add(ChangeItemProposalState(**proposal_data.model_dump()))
    session.flush()
    return revision


def create_change_item_revision(
    session: Session, data: ChangeItemRevisionInput
) -> ChangeItemRevision:
    identity = session.get(ChangeItem, data.change_item_id)
    if identity is None:
        raise ValueError(
            "Change Item identity must be created with an initial Proposal State"
        )
    if identity.change_case_id != data.change_case_id:
        raise ValueError("Change Item identity already belongs to another Change Case")
    if session.get(ChangeItemProposalState, data.change_item_id) is None:
        raise ValueError("Change Item identity has no Proposal State")
    return _insert_change_item_revision(session, data)


def _insert_change_item_revision(
    session: Session, data: ChangeItemRevisionInput
) -> ChangeItemRevision:
    existing = session.get(
        ChangeItemRevision, (data.change_item_id, data.change_item_revision)
    )
    if existing is not None:
        raise ValueError("Change Item revision already exists and cannot be overwritten")

    revision_number = int(data.change_item_revision[1:])
    existing_labels = list(
        session.scalars(
            select(ChangeItemRevision.change_item_revision).where(
                ChangeItemRevision.change_item_id == data.change_item_id
            )
        )
    )
    if existing_labels and revision_number <= max(
        int(label[1:]) for label in existing_labels
    ):
        raise ValueError("Change Item revision numbers must be strictly increasing")

    record = ChangeItemRevision(**data.model_dump())
    session.add(record)
    session.flush()
    return record


def set_proposal_state(
    session: Session, data: ProposalStateInput
) -> ChangeItemProposalState:
    revision = session.get(
        ChangeItemRevision, (data.change_item_id, data.selected_revision)
    )
    if revision is None or revision.change_case_id != data.change_case_id:
        raise ValueError(
            "selected revision does not belong to the Change Item and Change Case"
        )

    state = session.get(ChangeItemProposalState, data.change_item_id)
    values = data.model_dump()
    if state is None:
        state = ChangeItemProposalState(**values)
        session.add(state)
    else:
        if state.change_case_id != data.change_case_id:
            raise ValueError("Proposal State Change Item belongs to another Change Case")
        for field, value in values.items():
            setattr(state, field, value)
    session.flush()
    return state


def active_proposed_change_scope(
    session: Session, change_case_id: str
) -> list[ChangeItemRevision]:
    statement = (
        select(ChangeItemRevision)
        .join(
            ChangeItemProposalState,
            (ChangeItemProposalState.change_item_id == ChangeItemRevision.change_item_id)
            & (
                ChangeItemProposalState.selected_revision
                == ChangeItemRevision.change_item_revision
            )
            & (ChangeItemProposalState.change_case_id == ChangeItemRevision.change_case_id),
        )
        .where(
            ChangeItemRevision.change_case_id == change_case_id,
            ChangeItemProposalState.proposal_state == "Active",
        )
        .order_by(ChangeItemRevision.change_item_id)
    )
    return list(session.scalars(statement))


def create_open_item(session: Session, data: OpenItemInput) -> OpenItem:
    record = OpenItem(**data.model_dump())
    session.add(record)
    session.flush()
    return record
