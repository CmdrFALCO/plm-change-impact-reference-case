from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from plm_ref.application.baseline import (
    BaselineReuseInputs,
    load_frozen_baseline_fixture,
    reuse_assessment_baseline,
)
from plm_ref.application.change_case import (
    ChangeCaseInput,
    ChangeItemRevisionInput,
    ProposalStateInput,
    create_change_case,
    create_change_item,
)
from plm_ref.application.overlay import (
    OverlayChangeItemMembershipInput,
    OverlayRevisionInput,
    construct_candidate_overlay,
    create_overlay_revision,
    evaluate_overlay_execution_eligibility,
    materialize_overlay_revision,
)
from plm_ref.application.source_projection import load_shared_source_fixture
from plm_ref.domain.errors import (
    ImmutableRecordError,
    OverlayExecutionEligibilityError,
)
from plm_ref.infrastructure.db.base import Base
from plm_ref.infrastructure.db.guards import assert_change_item_revision_mutable
from plm_ref.infrastructure.db.models import (
    BaselineMember,
    ChangeItemRevision,
    OverlayChangeItemMembership,
    OverlayLocalObject,
    OverlayRevision,
    ProductVersion,
)
from plm_ref.infrastructure.db.session import create_sqlite_engine


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _utc_token(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


SCENARIOS = {
    "A": {
        "case_id": "CHG-A01",
        "item_id": "CI-A01",
        "baseline_id": "BL-A01",
        "overlay_id": "OV-A01",
        "overlay_object_id": "OVOBJ-A01-PV",
        "created_at": "2026-08-25T19:00:00Z",
        "revision_created_at": "2026-08-25T19:02:00Z",
        "proposal_changed_at": "2026-08-25T19:03:00Z",
        "owner": "Change Owner A",
        "material": "MC-A-01",
        "scope": 'CoolingType = "Liquid"',
        "trigger": "Synthetic supplier process change",
    },
    "B": {
        "case_id": "CHG-B01",
        "item_id": "CI-B01",
        "baseline_id": "BL-B01",
        "overlay_id": "OV-B01",
        "overlay_object_id": "OVOBJ-B01-PV",
        "created_at": "2026-08-25T20:10:00Z",
        "revision_created_at": "2026-08-25T20:12:00Z",
        "proposal_changed_at": "2026-08-25T20:13:00Z",
        "owner": "Change Owner B",
        "material": "MC-B-01",
        "scope": 'CoolingType = "Liquid" AND PackFamily = "LongRange"',
        "trigger": "Synthetic supplier process change",
    },
    "C": {
        "case_id": "CHG-C01",
        "item_id": "CI-C01",
        "baseline_id": "BL-C01",
        "overlay_id": "OV-C01",
        "overlay_object_id": "OVOBJ-C01-PV",
        "created_at": "2026-08-25T21:30:00Z",
        "revision_created_at": "2026-08-25T21:32:00Z",
        "proposal_changed_at": "2026-08-25T21:33:00Z",
        "owner": "Change Owner C",
        "material": "MC-C-01",
        "scope": 'CoolingType = "Liquid"',
        "trigger": (
            "Synthetic supplier process change with elevated authority classification"
        ),
    },
}

FROZEN_OVERLAY_CREATED_AT = {
    "OV-A01": "2026-08-25T19:20:00Z",
    "OV-B01": "2026-08-25T20:30:00Z",
    "OV-B02": "2026-08-25T21:10:00Z",
    "OV-C01": "2026-08-25T21:50:00Z",
}


def _case(scenario: str) -> ChangeCaseInput:
    values = SCENARIOS[scenario]
    return ChangeCaseInput(
        change_case_id=values["case_id"],
        title=f"{values['case_id']} frozen case",
        trigger=values["trigger"],
        rationale="Frozen scenario rationale.",
        change_owner=values["owner"],
        case_state="Open",
        process_iteration=1,
        created_at=_dt(values["created_at"]),
        closed_at=None,
    )


def _revise(
    scenario: str,
    *,
    item_id: str | None = None,
    item_revision: str = "r1",
    current_revision: str = "A",
    proposed_revision: str = "B",
) -> ChangeItemRevisionInput:
    values = SCENARIOS[scenario]
    source_item_id = item_id or values["item_id"]
    return ChangeItemRevisionInput(
        change_item_id=source_item_id,
        change_item_revision=item_revision,
        change_case_id=values["case_id"],
        action="Revise Product State",
        target_type="Product Version",
        target_id="PV-003",
        current_state_reference={
            "product_version_id": "PV-003",
            "revision": current_revision,
            "iteration": "1",
        },
        proposed_state_payload={
            "product_element_id": "PE-003",
            "proposed_revision": proposed_revision,
            "proposed_iteration": "1",
            "supersedes_product_version_id": "PV-003",
            "material_characteristic": values["material"],
            "validated_configuration_scope": values["scope"],
            "intended_function_change": False,
        },
        reason="Frozen synthetic change.",
        owner=values["owner"],
        configuration_context_id="CFG-001",
        intended_effectivity={
            "effectivity_type": "Planned Engineering Effective Date",
            "planned_effective_date": "2026-11-01",
        },
        revision_created_at=_dt(values["revision_created_at"]),
    )


def _applicability(
    *, applicability_rule_id: str = "APP-001"
) -> ChangeItemRevisionInput:
    return ChangeItemRevisionInput(
        change_item_id="CI-B02",
        change_item_revision="r1",
        change_case_id="CHG-B01",
        action="Change Applicability",
        target_type="Product Structure Occurrence",
        target_id="PSO-002",
        current_state_reference={
            "occurrence_id": "PSO-002",
            "applicability_rule_id": applicability_rule_id,
            "applicability_rule_version": "1",
        },
        proposed_state_payload={
            "applicability_rule": {
                "rule_id": "APP-B02",
                "expression": (
                    'CoolingType = "Liquid" AND PackFamily = "LongRange"'
                ),
                "rule_version": "1",
            }
        },
        reason="Align occurrence applicability with the proposed state.",
        owner="Change Owner B",
        configuration_context_id="CFG-001",
        intended_effectivity={
            "effectivity_type": "Planned Engineering Effective Date",
            "planned_effective_date": "2026-11-01",
        },
        revision_created_at=_dt("2026-08-25T21:05:00Z"),
    )


def _proposal(
    scenario: str,
    *,
    item_id: str | None = None,
    selected_revision: str = "r1",
) -> ProposalStateInput:
    values = SCENARIOS[scenario]
    return ProposalStateInput(
        change_item_id=item_id or values["item_id"],
        change_case_id=values["case_id"],
        selected_revision=selected_revision,
        proposal_state="Active",
        state_changed_at=_dt(values["proposal_changed_at"]),
        state_changed_by=values["owner"],
    )


def _overlay(scenario: str, *, overlay_id: str | None = None) -> OverlayRevisionInput:
    values = SCENARIOS[scenario]
    selected_overlay_id = overlay_id or values["overlay_id"]
    return OverlayRevisionInput(
        overlay_revision_id=selected_overlay_id,
        change_case_id=values["case_id"],
        created_at=_dt(FROZEN_OVERLAY_CREATED_AT[selected_overlay_id]),
    )


def _prepare_initial_scenario(session: Session, scenario: str) -> None:
    create_change_case(session, _case(scenario))
    create_change_item(
        session,
        _revise(scenario),
        _proposal(scenario),
    )
    load_frozen_baseline_fixture(session, scenario)


@pytest.fixture
def engine(tmp_path: Path):
    database_engine = create_sqlite_engine(tmp_path / "g04.db")
    Base.metadata.create_all(database_engine)
    try:
        with Session(database_engine) as session, session.begin():
            load_shared_source_fixture(session)
        yield database_engine
    finally:
        database_engine.dispose()


def _migration_engine(tmp_path: Path):
    database_path = tmp_path / "migration.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{database_path}")
    command.upgrade(config, "mig_004")
    return create_sqlite_engine(database_path), config


def test_mig_004_applies_with_required_tables_constraints_and_trigger_subset(
    tmp_path: Path,
) -> None:
    database_engine, _ = _migration_engine(tmp_path)
    try:
        table_names = set(inspect(database_engine).get_table_names())
        assert {
            "overlay_revisions",
            "overlay_change_item_memberships",
            "overlay_local_objects",
        } <= table_names
        membership_unique = {
            constraint["name"]
            for constraint in inspect(database_engine).get_unique_constraints(
                "overlay_change_item_memberships"
            )
        }
        assert "uq_overlay_membership_revision" in membership_unique
        with database_engine.connect() as connection:
            triggers = {
                row.name: row.sql
                for row in connection.execute(
                    text(
                        "SELECT name, sql FROM sqlite_master "
                        "WHERE type='trigger' AND name LIKE "
                        "'trg_change_item_revisions_overlay_%'"
                    )
                )
            }
            assert set(triggers) == {
                "trg_change_item_revisions_overlay_update_immutable",
                "trg_change_item_revisions_overlay_delete_immutable",
            }
            assert all(
                "overlay_change_item_memberships" in sql
                for sql in triggers.values()
            )
            assert connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one() == "mig_004"
    finally:
        database_engine.dispose()


def test_mig_004_downgrade_removes_only_its_tables_and_triggers(
    tmp_path: Path,
) -> None:
    database_engine, config = _migration_engine(tmp_path)
    database_engine.dispose()
    command.downgrade(config, "mig_003")
    database_engine = create_sqlite_engine(tmp_path / "migration.db")
    try:
        table_names = set(inspect(database_engine).get_table_names())
        assert "assessment_baselines" in table_names
        assert "overlay_revisions" not in table_names
        with database_engine.connect() as connection:
            assert connection.execute(
                text(
                    "SELECT COUNT(*) FROM sqlite_master "
                    "WHERE type='trigger' AND name LIKE "
                    "'trg_change_item_revisions_overlay_%'"
                )
            ).scalar_one() == 0
            assert connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one() == "mig_003"
    finally:
        database_engine.dispose()


@pytest.mark.parametrize("scenario", ["A", "B", "C"])
def test_initial_frozen_overlays_pass_and_materialize_exactly(
    engine, scenario: str
) -> None:
    values = SCENARIOS[scenario]
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, scenario)
        candidate = construct_candidate_overlay(session, _overlay(scenario))
        result = evaluate_overlay_execution_eligibility(
            session, values["baseline_id"], candidate
        )
        assert result.passed
        assert result.active_change_items == (f"{values['item_id']}:r1",)
        materialize_overlay_revision(session, values["baseline_id"], candidate)

    with Session(engine) as session:
        overlay = session.get(OverlayRevision, values["overlay_id"])
        assert overlay is not None
        assert overlay.change_case_id == values["case_id"]
        assert _utc_token(overlay.created_at) == FROZEN_OVERLAY_CREATED_AT[
            values["overlay_id"]
        ]
        memberships = list(
            session.scalars(
                select(OverlayChangeItemMembership).where(
                    OverlayChangeItemMembership.overlay_revision_id
                    == values["overlay_id"]
                )
            )
        )
        assert [
            (member.change_item_id, member.change_item_revision)
            for member in memberships
        ] == [(values["item_id"], "r1")]
        objects = list(
            session.scalars(
                select(OverlayLocalObject).where(
                    OverlayLocalObject.overlay_revision_id == values["overlay_id"]
                )
            )
        )
        assert len(objects) == 1
        assert objects[0].overlay_local_object_id == values["overlay_object_id"]
        assert objects[0].object_type == "Product Version"
        assert objects[0].state_payload == {
            "product_element_id": "PE-003",
            "proposed_revision": "B",
            "proposed_iteration": "1",
            "supersedes_product_version_id": "PV-003",
            "material_characteristic": values["material"],
            "validated_configuration_scope": values["scope"],
            "intended_function_change": False,
        }
        authoritative = session.get(ProductVersion, "PV-003")
        assert authoritative is not None
        assert (authoritative.revision, authoritative.iteration) == ("A", "1")


def test_ov_b02_passes_against_reused_bl_b01_and_materializes_exact_scope(
    engine,
) -> None:
    reuse_inputs = BaselineReuseInputs(
        authoritative_current_state_unchanged=True,
        baseline_scope_still_sufficient=True,
        configuration_context_still_valid=True,
        effectivity_context_still_valid=True,
        extraction_basis_still_accepted=True,
    )
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "B")
        create_overlay_revision(session, "BL-B01", _overlay("B"))
        create_change_item(
            session,
            _applicability(),
            _proposal("B", item_id="CI-B02"),
        )
        reused = reuse_assessment_baseline(
            session, "BL-B01", "CHG-B01", reuse_inputs
        )
        assert reused.assessment_baseline_id == "BL-B01"
        candidate = construct_candidate_overlay(
            session,
            _overlay("B", overlay_id="OV-B02"),
            local_object_ids={
                "CI-B01": "OVOBJ-B02-PV",
                "CI-B02": "OVOBJ-B02-PSO",
            },
        )
        assert _utc_token(candidate.revision.created_at) == "2026-08-25T21:10:00Z"
        result = evaluate_overlay_execution_eligibility(
            session, reused.assessment_baseline_id, candidate
        )
        assert result.passed
        assert result.active_change_items == ("CI-B01:r1", "CI-B02:r1")
        materialize_overlay_revision(
            session, reused.assessment_baseline_id, candidate
        )

    with Session(engine) as session:
        b01 = session.get(OverlayRevision, "OV-B01")
        b02 = session.get(OverlayRevision, "OV-B02")
        assert b01 is not None and b02 is not None
        assert _utc_token(b01.created_at) == FROZEN_OVERLAY_CREATED_AT["OV-B01"]
        assert _utc_token(b02.created_at) == FROZEN_OVERLAY_CREATED_AT["OV-B02"]
        memberships = list(
            session.execute(
                select(
                    OverlayChangeItemMembership.overlay_revision_id,
                    OverlayChangeItemMembership.change_item_id,
                    OverlayChangeItemMembership.change_item_revision,
                ).order_by(
                    OverlayChangeItemMembership.overlay_revision_id,
                    OverlayChangeItemMembership.change_item_id,
                )
            )
        )
        assert memberships == [
            ("OV-B01", "CI-B01", "r1"),
            ("OV-B02", "CI-B01", "r1"),
            ("OV-B02", "CI-B02", "r1"),
        ]
        objects = list(
            session.scalars(
                select(OverlayLocalObject)
                .where(OverlayLocalObject.overlay_revision_id == "OV-B02")
                .order_by(OverlayLocalObject.overlay_local_object_id)
            )
        )
        assert [item.overlay_local_object_id for item in objects] == [
            "OVOBJ-B02-PSO",
            "OVOBJ-B02-PV",
        ]
        occurrence = objects[0]
        assert occurrence.state_payload == {
            "occurrence_id": "PSO-002",
            "parent_product_version_id": "PV-002",
            "child_product_version_reference": "OVOBJ-B02-PV",
            "position": "020",
            "quantity": 1,
            "unit": "EA",
            "applicability_rule": {
                "rule_id": "APP-B02",
                "expression": (
                    'CoolingType = "Liquid" AND PackFamily = "LongRange"'
                ),
                "rule_version": "1",
            },
            "effectivity_specification": {
                "effectivity_type": "Planned Engineering Effective Date",
                "planned_effective_date": "2026-11-01",
            },
        }


def test_exact_active_membership_rejects_missing_and_duplicate_identity(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "B")
        create_change_item(
            session,
            _applicability(),
            _proposal("B", item_id="CI-B02"),
        )
        revision = _overlay("B", overlay_id="OV-B02")
        incomplete = construct_candidate_overlay(
            session,
            revision,
            memberships=[
                OverlayChangeItemMembershipInput(
                    overlay_revision_id="OV-B02",
                    change_item_id="CI-B01",
                    change_item_revision="r1",
                )
            ],
        )
        result = evaluate_overlay_execution_eligibility(
            session, "BL-B01", incomplete
        )
        assert not result.passed
        assert any("exactly match" in reason for reason in result.reasons)

        duplicate = construct_candidate_overlay(
            session,
            revision,
            memberships=[
                OverlayChangeItemMembershipInput(
                    overlay_revision_id="OV-B02",
                    change_item_id="CI-B01",
                    change_item_revision="r1",
                ),
                OverlayChangeItemMembershipInput(
                    overlay_revision_id="OV-B02",
                    change_item_id="CI-B01",
                    change_item_revision="r1",
                ),
                OverlayChangeItemMembershipInput(
                    overlay_revision_id="OV-B02",
                    change_item_id="CI-B02",
                    change_item_revision="r1",
                ),
            ],
        )
        result = evaluate_overlay_execution_eligibility(
            session, "BL-B01", duplicate
        )
        assert not result.passed
        assert any("duplicate Change Item identity" in reason for reason in result.reasons)


def test_target_absent_from_baseline_fails_before_materialization(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        member = session.scalar(
            select(BaselineMember).where(
                BaselineMember.assessment_baseline_id == "BL-A01",
                BaselineMember.object_type == "Product Version",
                BaselineMember.object_id == "PV-003",
            )
        )
        assert member is not None
        session.delete(member)
        session.flush()
        candidate = construct_candidate_overlay(session, _overlay("A"))
        result = evaluate_overlay_execution_eligibility(
            session, "BL-A01", candidate
        )
        assert not result.passed
        assert any("absent from the baseline" in reason for reason in result.reasons)
        with pytest.raises(OverlayExecutionEligibilityError):
            materialize_overlay_revision(session, "BL-A01", candidate)
        assert session.get(OverlayRevision, "OV-A01") is None


def test_baseline_current_reference_mismatch_fails(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        member = session.scalar(
            select(BaselineMember).where(
                BaselineMember.assessment_baseline_id == "BL-A01",
                BaselineMember.object_type == "Product Version",
                BaselineMember.object_id == "PV-003",
            )
        )
        assert member is not None
        snapshot = dict(member.snapshot_payload)
        snapshot["revision"] = "Z"
        member.snapshot_payload = snapshot
        session.flush()
        result = evaluate_overlay_execution_eligibility(
            session,
            "BL-A01",
            construct_candidate_overlay(session, _overlay("A")),
        )
        assert not result.passed
        assert any("does not match current_state_reference" in reason for reason in result.reasons)


def test_authoritative_successor_identity_collision_fails(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        item = session.get(ChangeItemRevision, ("CI-A01", "r1"))
        assert item is not None
        proposed = dict(item.proposed_state_payload)
        proposed["proposed_revision"] = "A"
        item.proposed_state_payload = proposed
        session.flush()
        result = evaluate_overlay_execution_eligibility(
            session,
            "BL-A01",
            construct_candidate_overlay(session, _overlay("A")),
        )
        assert not result.passed
        assert any("collides with authoritative" in reason for reason in result.reasons)


def test_successor_identity_collision_within_candidate_overlay_fails(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        create_change_item(
            session,
            _revise("A", item_id="CI-A02"),
            _proposal("A", item_id="CI-A02"),
        )
        candidate = construct_candidate_overlay(session, _overlay("A"))
        result = evaluate_overlay_execution_eligibility(
            session, "BL-A01", candidate
        )
        assert not result.passed
        assert any("collides within" in reason for reason in result.reasons)


def test_wrong_predecessor_applicability_fails_against_captured_occurrence(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "B")
        create_change_item(
            session,
            _applicability(applicability_rule_id="APP-WRONG"),
            _proposal("B", item_id="CI-B02"),
        )
        candidate = construct_candidate_overlay(
            session, _overlay("B", overlay_id="OV-B02")
        )
        result = evaluate_overlay_execution_eligibility(
            session, "BL-B01", candidate
        )
        assert not result.passed
        assert any(
            "predecessor Applicability Rule does not match" in reason
            for reason in result.reasons
        )


def test_same_case_membership_is_validated_before_commit(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        create_change_case(session, _case("C"))
        candidate = construct_candidate_overlay(
            session,
            OverlayRevisionInput(
                overlay_revision_id="OV-X01",
                change_case_id="CHG-C01",
                created_at=_dt("2026-08-25T21:50:00Z"),
            ),
            memberships=[
                OverlayChangeItemMembershipInput(
                    overlay_revision_id="OV-X01",
                    change_item_id="CI-A01",
                    change_item_revision="r1",
                )
            ],
        )
        result = evaluate_overlay_execution_eligibility(
            session, "BL-A01", candidate
        )
        assert not result.passed
        assert any("another Change Case" in reason for reason in result.reasons)
        assert session.get(OverlayRevision, "OV-X01") is None


def test_change_item_revision_is_immutable_after_overlay_reference(
    tmp_path: Path,
) -> None:
    database_engine, _ = _migration_engine(tmp_path)
    try:
        with Session(database_engine) as session, session.begin():
            load_shared_source_fixture(session)
            _prepare_initial_scenario(session, "A")
            create_overlay_revision(session, "BL-A01", _overlay("A"))

        with Session(database_engine) as session:
            with pytest.raises(ImmutableRecordError):
                assert_change_item_revision_mutable(session, "CI-A01", "r1")

        with database_engine.begin() as connection:
            with pytest.raises(
                IntegrityError, match="used Change Item Revision is immutable"
            ):
                connection.execute(
                    text(
                        "UPDATE change_item_revisions SET reason='Changed' "
                        "WHERE change_item_id='CI-A01' "
                        "AND change_item_revision='r1'"
                    )
                )
        with database_engine.begin() as connection:
            with pytest.raises(
                IntegrityError, match="used Change Item Revision is immutable"
            ):
                connection.execute(
                    text(
                        "DELETE FROM change_item_revisions "
                        "WHERE change_item_id='CI-A01' "
                        "AND change_item_revision='r1'"
                    )
                )
    finally:
        database_engine.dispose()
