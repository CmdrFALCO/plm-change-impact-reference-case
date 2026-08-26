from __future__ import annotations

import ast
import inspect
from datetime import datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from pydantic import ValidationError
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import plm_ref.application.gate_a as gate_a_module
from plm_ref.application.change_case import (
    ChangeCaseInput,
    ChangeItemRevisionInput,
    OpenItemInput,
    ProposalStateInput,
    active_proposed_change_scope,
    create_change_case,
    create_change_item,
    create_change_item_revision,
    create_open_item,
    set_proposal_state,
)
from plm_ref.application.gate_a import evaluate_gate_a
from plm_ref.infrastructure.db.base import Base
from plm_ref.infrastructure.db.models import (
    AssessmentBaseline,
    ConfigurationContext,
    ProductElement,
    ProductStructureOccurrence,
    ProductVersion,
)
from plm_ref.infrastructure.db.session import create_sqlite_engine

G02_TABLES = {
    "product_elements",
    "product_versions",
    "product_structure_occurrences",
    "configuration_contexts",
    "requirements",
    "evidence_records",
    "change_cases",
    "change_items",
    "change_item_revisions",
    "change_item_proposal_states",
    "open_items",
}


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _seed_source(session: Session) -> None:
    session.add_all(
        [
            ProductElement(
                product_element_id="PE-002",
                external_identifier="SYN-TMA-001",
                name="Thermal Management Assembly",
                element_type="Assembly",
                source_class="Product Data Source",
                source_identifier="PDS-PE-002",
                extraction_timestamp=_dt("2026-08-25T18:00:00Z"),
            ),
            ProductElement(
                product_element_id="PE-003",
                external_identifier="SYN-CP-001",
                name="Cooling Plate",
                element_type="Component",
                source_class="Product Data Source",
                source_identifier="PDS-PE-003",
                extraction_timestamp=_dt("2026-08-25T18:00:00Z"),
            ),
            ConfigurationContext(
                configuration_context_id="CFG-001",
                name="LongRange Liquid Configuration",
                feature_values={"PackFamily": "LongRange", "CoolingType": "Liquid"},
                completeness_state="Complete",
            ),
        ]
    )
    session.flush()
    session.add_all(
        [
            ProductVersion(
                product_version_id="PV-002",
                product_element_id="PE-002",
                revision="A",
                iteration="1",
                lifecycle_state="Current",
                is_baselined=True,
                supersedes_product_version_id=None,
                source_class="Product Data Source",
                source_identifier="PDS-PV-002-A1",
                extraction_timestamp=_dt("2026-08-25T18:00:00Z"),
            ),
            ProductVersion(
                product_version_id="PV-003",
                product_element_id="PE-003",
                revision="A",
                iteration="1",
                lifecycle_state="Current",
                is_baselined=True,
                supersedes_product_version_id=None,
                source_class="Product Data Source",
                source_identifier="PDS-PV-003-A1",
                extraction_timestamp=_dt("2026-08-25T18:00:00Z"),
            ),
        ]
    )
    session.flush()
    session.add(
        ProductStructureOccurrence(
            occurrence_id="PSO-002",
            parent_product_version_id="PV-002",
            child_product_version_id="PV-003",
            position="020",
            quantity=1,
            unit="EA",
            applicability_rule={
                "rule_id": "APP-001",
                "expression": 'CoolingType = "Liquid"',
                "rule_version": "1",
            },
            effectivity_specification={
                "effectivity_type": "Planned Engineering Effective Date",
                "planned_effective_date": "2026-11-01",
            },
            source_class="Product Data Source",
            source_identifier="PDS-PSO-002",
            extraction_timestamp=_dt("2026-08-25T18:00:00Z"),
        )
    )
    session.flush()


@pytest.fixture
def session(tmp_path: Path):
    engine = create_sqlite_engine(tmp_path / "g02.db")
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as database_session:
            _seed_source(database_session)
            database_session.commit()
            yield database_session
    finally:
        engine.dispose()


def _case(
    case_id: str,
    *,
    rationale: str = "Frozen rationale.",
    trigger: str = "Synthetic supplier process change",
) -> ChangeCaseInput:
    return ChangeCaseInput(
        change_case_id=case_id,
        title=f"{case_id} case",
        trigger=trigger,
        rationale=rationale,
        change_owner="Owner",
        case_state="Open",
        process_iteration=1,
        created_at=_dt("2026-08-25T19:00:00Z"),
        closed_at=None,
    )


def _revise(
    item_id: str,
    case_id: str,
    *,
    revision: str = "r1",
    target_id: str = "PV-003",
    context: str = "CFG-001",
    scope: str = 'CoolingType = "Liquid"',
) -> ChangeItemRevisionInput:
    return ChangeItemRevisionInput(
        change_item_id=item_id,
        change_item_revision=revision,
        change_case_id=case_id,
        action="Revise Product State",
        target_type="Product Version",
        target_id=target_id,
        current_state_reference={
            "product_version_id": "PV-003",
            "revision": "A",
            "iteration": "1",
        },
        proposed_state_payload={
            "product_element_id": "PE-003",
            "proposed_revision": "B",
            "proposed_iteration": "1",
            "supersedes_product_version_id": "PV-003",
            "material_characteristic": f"MC-{item_id}",
            "validated_configuration_scope": scope,
            "intended_function_change": False,
        },
        reason="Synthetic change.",
        owner="Owner",
        configuration_context_id=context,
        intended_effectivity={
            "effectivity_type": "Planned Engineering Effective Date",
            "planned_effective_date": "2026-11-01",
        },
        revision_created_at=_dt("2026-08-25T19:02:00Z"),
    )


def _applicability(case_id: str) -> ChangeItemRevisionInput:
    return ChangeItemRevisionInput(
        change_item_id="CI-B02",
        change_item_revision="r1",
        change_case_id=case_id,
        action="Change Applicability",
        target_type="Product Structure Occurrence",
        target_id="PSO-002",
        current_state_reference={
            "occurrence_id": "PSO-002",
            "applicability_rule_id": "APP-001",
            "applicability_rule_version": "1",
        },
        proposed_state_payload={
            "applicability_rule": {
                "rule_id": "APP-B02",
                "expression": 'CoolingType = "Liquid" AND PackFamily = "LongRange"',
                "rule_version": "1",
            }
        },
        reason="Align occurrence applicability.",
        owner="Owner",
        configuration_context_id="CFG-001",
        intended_effectivity={
            "effectivity_type": "Planned Engineering Effective Date",
            "planned_effective_date": "2026-11-01",
        },
        revision_created_at=_dt("2026-08-25T21:05:00Z"),
    )


def _proposal(
    item_id: str,
    case_id: str,
    *,
    revision: str = "r1",
    state: str = "Active",
) -> ProposalStateInput:
    return ProposalStateInput(
        change_item_id=item_id,
        change_case_id=case_id,
        selected_revision=revision,
        proposal_state=state,
        state_changed_at=_dt("2026-08-25T19:03:00Z"),
        state_changed_by="Owner",
    )


def _load_revise(session: Session, case_id: str, item_id: str, **kwargs) -> None:
    create_change_case(
        session,
        _case(
            case_id,
            trigger=kwargs.pop("trigger", "Synthetic supplier process change"),
        ),
    )
    create_change_item(
        session,
        _revise(item_id, case_id, **kwargs),
        _proposal(item_id, case_id),
    )


def test_mig_002_applies_from_empty_database_and_remains_revision_two(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "migration.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{database_path}")
    command.upgrade(config, "mig_002")

    engine = create_sqlite_engine(database_path)
    try:
        assert set(sa_inspect(engine).get_table_names()) == G02_TABLES | {
            "alembic_version"
        }
        with engine.connect() as connection:
            assert connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one() == "mig_002"
    finally:
        engine.dispose()


def test_all_frozen_gate_a_paths_pass_without_baseline_rows(session: Session) -> None:
    _load_revise(session, "CHG-A01", "CI-A01")
    assert evaluate_gate_a(session, "CHG-A01").passed

    _load_revise(
        session,
        "CHG-B01",
        "CI-B01",
        scope='CoolingType = "Liquid" AND PackFamily = "LongRange"',
    )
    assert evaluate_gate_a(session, "CHG-B01").passed
    create_change_item(
        session,
        _applicability("CHG-B01"),
        _proposal("CI-B02", "CHG-B01"),
    )
    amended = evaluate_gate_a(session, "CHG-B01")
    assert amended.passed
    assert amended.active_change_items == ("CI-B01:r1", "CI-B02:r1")

    _load_revise(
        session,
        "CHG-C01",
        "CI-C01",
        trigger="Synthetic supplier process change with elevated authority classification",
    )
    assert evaluate_gate_a(session, "CHG-C01").passed
    assert session.scalar(
        select(AssessmentBaseline.assessment_baseline_id).limit(1)
    ) is None


def test_gate_a_module_has_no_baseline_dependency(session: Session) -> None:
    _load_revise(session, "CHG-X00", "CI-X00")
    result = evaluate_gate_a(session, "CHG-X00")
    assert result.baseline_membership_evaluated_at_gate_a is False

    tree = ast.parse(inspect.getsource(gate_a_module))
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    assert all("baseline" not in name.lower() for name in imported_modules)


def test_malformed_target_fails(session: Session) -> None:
    _load_revise(session, "CHG-X01", "CI-X01", target_id="PV-MISSING")
    assert not evaluate_gate_a(session, "CHG-X01").passed


def test_missing_rationale_fails(session: Session) -> None:
    create_change_case(session, _case("CHG-X02", rationale="   "))
    create_change_item(
        session,
        _revise("CI-X02", "CHG-X02"),
        _proposal("CI-X02", "CHG-X02"),
    )
    assert not evaluate_gate_a(session, "CHG-X02").passed


def test_invalid_context_fails(session: Session) -> None:
    session.add(
        ConfigurationContext(
            configuration_context_id="CFG-UNKNOWN",
            name="Unknown",
            feature_values={"PackFamily": "LongRange", "CoolingType": "Liquid"},
            completeness_state="Unknown",
        )
    )
    session.flush()
    _load_revise(session, "CHG-X03", "CI-X03", context="CFG-UNKNOWN")
    assert not evaluate_gate_a(session, "CHG-X03").passed


def test_blocking_initial_distribution_open_item_fails(session: Session) -> None:
    _load_revise(session, "CHG-X04", "CI-X04")
    create_open_item(
        session,
        OpenItemInput(
            open_item_id="OI-X04",
            change_case_id="CHG-X04",
            source_type="Change Case",
            source_id="CHG-X04",
            item_type="Information Gap",
            description="Missing input",
            owner="Owner",
            status="Open",
            blocking_class="Blocking",
            required_before_stage="Initial Distribution",
            resolution_evidence_reference=None,
            created_at=_dt("2026-08-25T19:04:00Z"),
            closed_at=None,
        ),
    )
    assert not evaluate_gate_a(session, "CHG-X04").passed


def test_duplicate_revision_is_rejected(session: Session) -> None:
    _load_revise(session, "CHG-X05", "CI-X05")
    with pytest.raises(ValueError, match="already exists"):
        create_change_item_revision(session, _revise("CI-X05", "CHG-X05"))


def test_revision_numbers_must_strictly_increase(session: Session) -> None:
    create_change_case(session, _case("CHG-X06"))
    create_change_item(
        session,
        _revise("CI-X06", "CHG-X06", revision="r1"),
        _proposal("CI-X06", "CHG-X06", revision="r1"),
    )
    create_change_item_revision(
        session,
        _revise("CI-X06", "CHG-X06", revision="r3"),
    )
    with pytest.raises(ValueError, match="strictly increasing"):
        create_change_item_revision(
            session,
            _revise("CI-X06", "CHG-X06", revision="r2"),
        )


def test_removed_from_proposal_is_excluded_from_active_scope(session: Session) -> None:
    _load_revise(session, "CHG-X07", "CI-X07")
    set_proposal_state(
        session,
        _proposal("CI-X07", "CHG-X07", state="Removed from Proposal"),
    )
    assert active_proposed_change_scope(session, "CHG-X07") == []
    assert not evaluate_gate_a(session, "CHG-X07").passed


def test_action_payloads_are_bounded() -> None:
    payload = _revise("CI-X08", "CHG-X08").model_dump()
    payload["proposed_state_payload"]["unexpected"] = "forbidden"
    with pytest.raises(ValidationError):
        ChangeItemRevisionInput.model_validate(payload)


def test_cross_case_selected_revision_is_rejected_by_service(session: Session) -> None:
    _load_revise(session, "CHG-X09", "CI-X09")
    create_change_case(session, _case("CHG-X10"))
    with pytest.raises(ValueError, match="does not belong"):
        set_proposal_state(session, _proposal("CI-X09", "CHG-X10"))


def test_cross_case_selected_revision_is_rejected_by_database(session: Session) -> None:
    _load_revise(session, "CHG-X11", "CI-X11")
    create_change_case(session, _case("CHG-X12"))
    with pytest.raises(IntegrityError):
        session.execute(
            text(
                "UPDATE change_item_proposal_states SET change_case_id='CHG-X12' "
                "WHERE change_item_id='CI-X11'"
            )
        )
        session.flush()
    session.rollback()
