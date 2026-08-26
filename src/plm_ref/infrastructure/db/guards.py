from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from plm_ref.domain.errors import ImmutableRecordError
from plm_ref.infrastructure.db.models import BaselineMember, ProductVersion


def is_product_version_captured_in_baseline(session: Session, product_version_id: str) -> bool:
    statement = select(BaselineMember.baseline_member_id).where(
        BaselineMember.object_type == "Product Version",
        BaselineMember.object_id == product_version_id,
    )
    return session.execute(statement.limit(1)).scalar_one_or_none() is not None


def assert_product_version_mutable(session: Session, product_version_id: str) -> ProductVersion:
    product_version = session.get(ProductVersion, product_version_id)
    if product_version is None:
        raise ValueError(f"Product Version {product_version_id} does not exist")
    if is_product_version_captured_in_baseline(session, product_version_id):
        raise ImmutableRecordError(
            f"Product Version {product_version_id} is immutable because it is captured in a baseline"
        )
    return product_version


def update_product_version_lifecycle_state(
    session: Session, product_version_id: str, lifecycle_state: str
) -> ProductVersion:
    product_version = assert_product_version_mutable(session, product_version_id)
    product_version.lifecycle_state = lifecycle_state
    session.flush()
    return product_version


def delete_product_version(session: Session, product_version_id: str) -> None:
    product_version = assert_product_version_mutable(session, product_version_id)
    session.delete(product_version)
    session.flush()
