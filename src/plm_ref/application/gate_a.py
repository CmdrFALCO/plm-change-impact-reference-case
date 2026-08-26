from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from plm_ref.application.change_case import active_proposed_change_scope
from plm_ref.domain.payloads import (
    ChangeApplicabilityCurrentReference,
    ReviseProductStateCurrentReference,
)
from plm_ref.infrastructure.db.models import (
    ChangeCase,
    ConfigurationContext,
    OpenItem,
    ProductStructureOccurrence,
    ProductVersion,
)


@dataclass(frozen=True)
class GateAResult:
    status: str
    reasons: tuple[str, ...]
    active_change_items: tuple[str, ...]
    baseline_membership_evaluated_at_gate_a: bool = False

    @property
    def passed(self) -> bool:
        return self.status == "Pass"


def evaluate_gate_a(session: Session, change_case_id: str) -> GateAResult:
    reasons: list[str] = []
    change_case = session.get(ChangeCase, change_case_id)
    if change_case is None:
        return GateAResult("Fail", ("Change Case does not exist",), ())

    scope = active_proposed_change_scope(session, change_case_id)
    active_ids = tuple(
        f"{item.change_item_id}:{item.change_item_revision}" for item in scope
    )
    if not scope:
        reasons.append("No Active Change Item Proposal State exists")

    if not change_case.rationale.strip():
        reasons.append("Change Case rationale is empty")

    blocker = session.scalar(
        select(OpenItem.open_item_id)
        .where(
            OpenItem.change_case_id == change_case_id,
            OpenItem.blocking_class == "Blocking",
            OpenItem.required_before_stage == "Initial Distribution",
            OpenItem.status != "Resolved",
        )
        .limit(1)
    )
    if blocker is not None:
        reasons.append(f"Blocking Initial Distribution Open Item exists: {blocker}")

    for item in scope:
        context = session.get(ConfigurationContext, item.configuration_context_id)
        if context is None or context.completeness_state not in {"Complete", "Partial"}:
            reasons.append(
                f"{item.change_item_id}:{item.change_item_revision} has invalid "
                "Configuration Context"
            )

        if item.action == "Revise Product State":
            _validate_revise_product_state(session, item, reasons)
        elif item.action == "Change Applicability":
            _validate_change_applicability(session, item, reasons)
        else:
            reasons.append(
                f"{item.change_item_id}:{item.change_item_revision} uses unsupported action"
            )

    return GateAResult(
        status="Pass" if not reasons else "Fail",
        reasons=tuple(reasons),
        active_change_items=active_ids,
    )


def _validate_revise_product_state(
    session: Session, item, reasons: list[str]
) -> None:
    key = f"{item.change_item_id}:{item.change_item_revision}"
    if item.target_type != "Product Version":
        reasons.append(f"{key} target_type must be Product Version")
        return

    target = session.get(ProductVersion, item.target_id)
    if target is None:
        reasons.append(f"{key} target Product Version does not exist")
        return

    try:
        current = ReviseProductStateCurrentReference.model_validate(
            item.current_state_reference
        )
    except ValidationError:
        reasons.append(f"{key} current-state Product Version reference is malformed")
        return

    if (
        current.product_version_id != item.target_id
        or current.revision != target.revision
        or current.iteration != target.iteration
    ):
        reasons.append(
            f"{key} current-state Product Version reference does not match target"
        )


def _validate_change_applicability(
    session: Session, item, reasons: list[str]
) -> None:
    key = f"{item.change_item_id}:{item.change_item_revision}"
    if item.target_type != "Product Structure Occurrence":
        reasons.append(f"{key} target_type must be Product Structure Occurrence")
        return

    target = session.get(ProductStructureOccurrence, item.target_id)
    if target is None:
        reasons.append(f"{key} target Product Structure Occurrence does not exist")
        return

    try:
        current = ChangeApplicabilityCurrentReference.model_validate(
            item.current_state_reference
        )
    except ValidationError:
        reasons.append(f"{key} current-state applicability reference is malformed")
        return

    if current.occurrence_id != item.target_id:
        reasons.append(f"{key} current-state occurrence reference does not match target")
    if (
        not current.applicability_rule_id.strip()
        or not current.applicability_rule_version.strip()
    ):
        reasons.append(f"{key} predecessor Applicability Rule reference is missing")
