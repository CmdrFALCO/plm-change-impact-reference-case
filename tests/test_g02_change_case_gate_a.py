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
from sqlalchemy import text
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


def _seed_gate_a_source(session: Session) -> None:
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
            _seed_gate_a_source(database_session)
            database_session.commit()
            yield database_session
    finally:
        engine.dispose()


def _case(
    case_id: str,
    title: str,
    trigger: str,
    rationale: str,
    owner: str,
    created_at: str,
) -> ChangeCaseInput:
    return ChangeCaseInput(
        change_case_id=case_id,
        title=title,
        trigger=trigger,
        rationale=rationale,
        change_owner=owner,
        case_state="Open",
        process_iteration=1,
        created_at=_dt(created_at),
        closed_at=None,
    )


def _revise_product_state(
    change_item_id: str,
    case_id: str,
    material_characteristic: str,
    validated_scope: str,
    reason: str,
    owner: str,
    created_at: str,
    *,
    target_id: str = "PV-003",
    target_type: str = "Product Version",
    configuration_context_id: str = "CFG-001",
) -> ChangeItemRevisionInput:
    return ChangeItemRevisionInput(
        change_item_id=change_item_id,
        change_item_revision="r1",
        change_case_id=case_id,
        action="Revise Product State",
        target_type=target_type,
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
            "material_characteristic": material_characteristic,
            "validated_configuration_scope": validated_scope,
            "intended_function_change": False,
        },
        reason=reason,
        owner=owner,
        configuration_context_id=configuration_context_id,
        intended_effectivity={
            "effectivity_type": "Planned Engineering Effective Date",
            "planned_effective_date": "2026-11-01",
        },
        revision_created_at=_dt(created_at),
    )


def _proposal(
    change_item_id: str, case_id: str, changed_at: str, changed_by: str
) -> ProposalStateInput:
    return ProposalStateInput(
        change_item_id=change_item_id,
        change_case_id=case_id,
        selected_revision="r1",
        proposal_state="Active",
        state_changed_at=_dt(changed_at),
        state_changed_by=changed_by,
    )


def _load_scenario_a(session: Session) -> None:
    create_change_case(
        session,
        _case(
            "CHG-A01",
            "Cooling Plate supplier-process material characteristic update",
            "Synthetic supplier process change",
            "Update one Cooling Plate material characteristic while preserving intended "
            "function and current applicability.",
            "Change Owner A",
            "2026-08-25T19:00:00Z",
        ),
    )
    create_change_item(
        session,
        _revise_product_state(
            "CI-A01",
            "CHG-A01",
            "MC-A-01",
            'CoolingType = "Liquid"',
            "Synthetic supplier process change.",
            "Change Owner A",
            "2026-08-25T19:02:00Z",
        ),
        _proposal("CI-A01", "CHG-A01", "2026-08-25T19:03:00Z", "Change Owner A"),
    )


def _load_scenario_b_initial(session: Session) -> None:
    create_change_case(
        session,
        _case(
            "CHG-B01",
            "Cooling Plate material revision requiring applicability scope amendment",
            "Synthetic supplier process change",
            "Evaluate a proposed Cooling Plate material characteristic whose validated "
            "configuration scope is narrower than the current occurrence applicability.",
            "Change Owner B",
            "2026-08-25T20:10:00Z",
        ),
    )
    create_change_item(
        session,
        _revise_product_state(
            "CI-B01",
            "CHG-B01",
            "MC-B-01",
            'CoolingType = "Liquid" AND PackFamily = "LongRange"',
            "Synthetic supplier process change with a narrower validated configuration scope.",
            "Change Owner B",
            "2026-08-25T20:12:00Z",
        ),
        _proposal("CI-B01", "CHG-B01", "2026-08-25T20:13:00Z", "Change Owner B"),
    )


def _scenario_b_applicability_revision() -> ChangeItemRevisionInput:
    return ChangeItemRevisionInput(
        change_item_id="CI-B02",
        change_item_revision="r1",
        change_case_id="CHG-B01",
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
        reason=(
            "Align occurrence applicability with the validated scope of the proposed "
            "Cooling Plate state."
        ),
        owner="Change Owner B",
        configuration_context_id="CFG-001",
        intended_effectivity={
            "effectivity_type": "Planned Engineering Effective Date",
            "planned_effective_date": "2026-11-01",
        },
        revision_created_at=_dt("2026-08-25T21:05:00Z"),
    )


def _load_scenario_c(session: Session) -> None:
    create_change_case(
        session,
        _case(
            "CHG-C01",
            "Cooling Plate change requiring Elevated authority",
            "Synthetic supplier process change with elevated authority classification",
            "Evaluate a bounded Cooling Plate product-state revision whose decision route "
            "requires Elevated authority.",
            "Change Owner C",
            "2026-08-25T21:30:00Z",
        ),
    )
    create_change_item(
        session,
        _revise_product_state(
            "CI-C01",
            "CHG-C01",
            "MC-C-01",
            'CoolingType = "Liquid"',
            "Synthetic change prepared under a route that requires Elevated authority.",
            "Change Owner C",
            "2026-08-25T21:32:00Z",
        ),
        _proposal("CI-C01", "CHG-C01", "2026-08-25T21:33:00Z", "Change Owner C"),
    )


def test_mig_002_applies_from_empty_database(tmp_path: Path) -> None:
    database_path = tmp_path / "migration.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{database_path}")
    command.upgrade(config, "head")

    engine = create_sqlite_engine(database_path)
    try:
        assert set(sa_inspect(engine).get_table_names()) == G02_TABLES | {"alembic_version"}
        with engine.connect() as connection:
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "mig_002"
    finally:
        engine.dispose()


def test_all_frozen_gate_a_paths_pass(session: Session) -> None:
    _load_scenario_a(session)
    assert evaluate_gate_a(session, "CHG-A01").passed

    _load_scenario_b_initial(session)
    assert evaluate_gate_a(session, "CHG-B01").passed
    create_change_item(
        session,
        _scenario_b_applicability_revision(),
        _proposal("CI-B02", "CHG-B01", "2026-08-25T21:06:00Z", "Change Owner B"),
    )
    amended = evaluate_gate_a(session, "CHG-B01")
    assert amended.passed
    assert amended.active_change_items == ("CI-B01:r1", "CI-B02:r1")

    _load_scenario_c(session)
    assert evaluate_gate_a(session, "CHG-C01").passed


def test_gate_a_does_not_require_a_baseline_row_or_module(session: Session) -> None:
    _load_scenario_a(session)
    table_names = set(
        session.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).scalars()
    )
    assert "assessment_baselines" not in table_names

    result = evaluate_gate_a(session, "CHG-A01")
    assert result.passed
    assert result.baseline_membership_evaluated_at_gate_a is False

    tree = ast.parse(inspect.getsource(gate_a_module))
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    assert all("baseline" not in module.lower() for module in imported_modules)


def test_malformed_target_fails_gate_a(session: Session) -> None:
    create_change_case(
        session,
        _case(
            "CHG-X01",
            "Malformed target case",
            "Synthetic supplier process change",
            "Rationale present.",
            "Change Owner X",
            "2026-08-25T19:00:00Z",
        ),
    )
    create_change_item(
        session,
        _revise_product_state(
            "CI-X01",
            "CHG-X01",
            "MC-X-01",
            'CoolingType = "Liquid"',
            "Synthetic change.",
            "Change Owner X",
            "2026-08-25T19:02:00Z",
            target_id="PV-MISSING",
        ),
        _proposal("CI-X01", "CHG-X01", "2026-08-25T19:03:00Z", "Change Owner X"),
    )
    assert not evaluate_gate_a(session, "CHG-X01").passed


def test_missing_rationale_fails_gate_a(session: Session) -> None:
    create_change_case(
        session,
        _case(
            "CHG-X02",
            "Missing rationale case",
            "Synthetic supplier process change",
            "   ",
            "Change Owner X",
            "2026-08-25T19:00:00Z",
        ),
    )
    create_change_item(
        session,
        _revise_product_state(
            "CI-X02",
            "CHG-X02",
            "MC-X-02",
            'CoolingType = "Liquid"',
            "Synthetic change.",
            "Change Owner X",
            "2026-08-25T19:02:00Z",
        ),
        _proposal("CI-X02", "CHG-X02", "2026-08-25T19:03:00Z", "Change Owner X"),
    )
    assert not evaluate_gate_a(session, "CHG-X02").passed


def test_invalid_configuration_context_fails_gate_a(session: Session) -> None:
    session.add(
        ConfigurationContext(
            configuration_context_id="CFG-UNKNOWN",
            name="Unknown configuration",
            feature_values={"PackFamily": "LongRange", "CoolingType": "Liquid"},
            completeness_state="Unknown",
        )
    )
    session.flush()
    create_change_case(
        session,
        _case(
            "CHG-X03",
            "Invalid context case",
            "Synthetic supplier process change",
            "Rationale present.",
            "Change Owner X",
            "2026-08-25T19:00:00Z",
        ),
    )
    create_change_item(
        session,
        _revise_product_state(
            "CI-X03",
            "CHG-X03",
            "MC-X-03",
            'CoolingType = "Liquid"',
            "Synthetic change.",
            "Change Owner X",
            "2026-08-25T19:02:00Z",
            configuration_context_id="CFG-UNKNOWN",
        ),
        _proposal("CI-X03", "CHG-X03", "2026-08-25T19:03:00Z", "Change Owner X"),
    )
    assert not evaluate_gate_a(session, "CHG-X03").passed


def test_blocking_initial_distribution_open_item_fails_gate_a(session: Session) -> None:
    _load_scenario_a(session)
    create_open_item(
        session,
        OpenItemInput(
            open_item_id="OI-X01",
            change_case_id="CHG-A01",
            source_type="Change Case",
            source_id="CHG-A01",
            item_type="Information Gap",
            description="Missing mandatory initial information.",
            owner="Change Owner A",
            status="Open",
            blocking_class="Blocking",
            required_before_stage="Initial Distribution",
            resolution_evidence_reference=None,
            created_at=_dt("2026-08-25T19:04:00Z"),
            closed_at=None,
        ),
    )
    assert not evaluate_gate_a(session, "CHG-A01").passed


def test_duplicate_revision_is_rejected(session: Session) -> None:
    _load_scenario_a(session)
    with pytest.raises(ValueError, match="already exists"):
        create_change_item_revision(
            session,
            _revise_product_state(
                "CI-A01",
                "CHG-A01",
                "MC-A-02",
                'CoolingType = "Liquid"',
                "Second synthetic revision.",
                "Change Owner A",
                "2026-08-25T19:05:00Z",
            ),
        )


def test_revision_numbers_are_strictly_increasing(session: Session) -> None:
    create_change_case(
        session,
        _case(
            "CHG-X04",
            "Revision-order case",
            "Synthetic supplier process change",
            "Rationale present.",
            "Change Owner X",
            "2026-08-25T19:00:00Z",
        ),
    )
    r1 = _revise_product_state(
        "CI-X04",
        "CHG-X04",
        "MC-X-04",
        'CoolingType = "Liquid"',
        "Synthetic change.",
        "Change Owner X",
        "2026-08-25T19:01:00Z",
    )
    create_change_item(
        session,
        r1,
        _proposal("CI-X04", "CHG-X04", "2026-08-25T19:01:30Z", "Change Owner X"),
    )
    r3 = ChangeItemRevisionInput.model_validate(
        {
            **r1.model_dump(),
            "change_item_revision": "r3",
            "revision_created_at": _dt("2026-08-25T19:02:00Z"),
        }
    )
    create_change_item_revision(session, r3)
    r2_late = ChangeItemRevisionInput.model_validate(
        {
            **r1.model_dump(),
            "change_item_revision": "r2",
            "revision_created_at": _dt("2026-08-25T19:03:00Z"),
        }
    )
    with pytest.raises(ValueError, match="strictly increasing"):
        create_change_item_revision(session, r2_late)


def test_cross_case_selected_revision_is_rejected_by_service_and_sql(session: Session) -> None:
    _load_scenario_a(session)
    create_change_case(
        session,
        _case(
            "CHG-X05",
            "Cross-case integrity case",
            "Synthetic supplier process change",
            "Rationale present.",
            "Change Owner X",
            "2026-08-25T19:00:00Z",
        ),
    )
    create_change_item(
        session,
        _revise_product_state(
            "CI-X05",
            "CHG-X05",
            "MC-X-05",
            'CoolingType = "Liquid"',
            "Synthetic change.",
            "Change Owner X",
            "2026-08-25T19:02:00Z",
        ),
        _proposal("CI-X05", "CHG-X05", "2026-08-25T19:03:00Z", "Change Owner X"),
    )

    with pytest.raises(ValueError, match="does not belong"):
        set_proposal_state(
            session,
            ProposalStateInput(
                change_item_id="CI-A01",
                change_case_id="CHG-X05",
                selected_revision="r1",
                proposal_state="Active",
                state_changed_at=_dt("2026-08-25T19:06:00Z"),
                state_changed_by="Change Owner X",
            ),
        )

    with pytest.raises(IntegrityError):
        session.execute(
            text(
                "UPDATE change_item_proposal_states "
                "SET change_case_id = 'CHG-A01' "
                "WHERE change_item_id = 'CI-X05'"
            )
        )
        session.flush()
    session.rollback()


def test_removed_proposal_is_excluded_from_active_scope(session: Session) -> None:
    _load_scenario_a(session)
    set_proposal_state(
        session,
        ProposalStateInput(
            change_item_id="CI-A01",
            change_case_id="CHG-A01",
            selected_revision="r1",
            proposal_state="Removed from Proposal",
            state_changed_at=_dt("2026-08-25T19:05:00Z"),
            state_changed_by="Change Owner A",
        ),
    )
    assert active_proposed_change_scope(session, "CHG-A01") == []
    assert not evaluate_gate_a(session, "CHG-A01").passed


def test_change_item_payloads_are_bounded() -> None:
    base = _revise_product_state(
        "CI-X06",
        "CHG-X06",
        "MC-X-06",
        'CoolingType = "Liquid"',
        "Synthetic change.",
        "Change Owner X",
        "2026-08-25T19:02:00Z",
    ).model_dump()
    base["current_state_reference"] = {
        "product_version_id": "PV-003",
        "revision": "A",
        "iteration": "1",
        "unexpected": "not allowed",
    }
    with pytest.raises(ValidationError):
        ChangeItemRevisionInput.model_validate(base)
