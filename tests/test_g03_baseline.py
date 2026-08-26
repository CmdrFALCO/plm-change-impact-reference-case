from __future__ import annotations

import importlib.util
from datetime import datetime
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from plm_ref.application.baseline import (
    BaselineReuseInputs,
    baseline_reuse_permitted,
    create_assessment_baseline,
    frozen_baseline_inputs,
    load_frozen_baseline_fixture,
    read_canonical_baseline_snapshots,
    reuse_assessment_baseline,
)
from plm_ref.domain.errors import ImmutableRecordError
from plm_ref.infrastructure.db.base import Base
from plm_ref.infrastructure.db.guards import (
    delete_product_version,
    is_product_version_captured_in_baseline,
    update_product_version_lifecycle_state,
)
from plm_ref.infrastructure.db.models import (
    AssessmentBaseline,
    BaselineMember,
    ChangeCase,
    ConfigurationContext,
    ProductElement,
    ProductStructureOccurrence,
    ProductVersion,
    Requirement,
)
from plm_ref.infrastructure.db.session import create_sqlite_engine

ROOT = Path(__file__).resolve().parents[1]
MIG_003_PATH = ROOT / "migrations" / "versions" / "mig_003_assessment_baseline.py"
PREVIOUS_TABLES = (
    "product_elements",
    "configuration_contexts",
    "product_versions",
    "product_structure_occurrences",
    "requirements",
    "evidence_records",
    "change_cases",
    "change_items",
    "change_item_revisions",
    "change_item_proposal_states",
    "open_items",
)


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
    requirements = [
        (
            "REQ-001",
            "Cooling Plate functional behaviour shall remain acceptable within the declared synthetic configuration scope.",
            "PE-003",
            "REQSRC-001",
        ),
        (
            "REQ-002",
            "Validation evidence used for a proposed Cooling Plate state shall be demonstrated as applicable to the evaluated state.",
            "PE-003",
            "REQSRC-002",
        ),
        (
            "REQ-003",
            "The proposed Cooling Plate state shall remain compatible with the declared synthetic manufacturing route.",
            "PE-003",
            "REQSRC-003",
        ),
        (
            "REQ-004",
            "Cooling Plate occurrence applicability shall not include configurations outside the validated scope of the selected Cooling Plate product state.",
            "PE-002",
            "REQSRC-004",
        ),
    ]
    session.add_all(
        [
            Requirement(
                requirement_id=requirement_id,
                requirement_revision="1",
                text=requirement_text,
                allocated_product_element_id=allocated_product_element_id,
                source_class="Requirements Source",
                source_identifier=source_identifier,
                extraction_timestamp=_dt("2026-08-25T18:05:00Z"),
            )
            for (
                requirement_id,
                requirement_text,
                allocated_product_element_id,
                source_identifier,
            ) in requirements
        ]
    )
    session.flush()


def _seed_cases(session: Session) -> None:
    for case_id, created_at in [
        ("CHG-A01", "2026-08-25T19:00:00Z"),
        ("CHG-B01", "2026-08-25T20:10:00Z"),
        ("CHG-C01", "2026-08-25T21:30:00Z"),
    ]:
        session.add(
            ChangeCase(
                change_case_id=case_id,
                title=f"{case_id} synthetic case",
                trigger="Synthetic supplier process change",
                rationale="Frozen test rationale.",
                change_owner="Synthetic Change Owner",
                case_state="Open",
                process_iteration=1,
                created_at=_dt(created_at),
                closed_at=None,
            )
        )
    session.flush()


def _seed(session: Session) -> None:
    _seed_source(session)
    _seed_cases(session)


@pytest.fixture
def engine(tmp_path: Path):
    engine = create_sqlite_engine(tmp_path / "g03.db")
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            _seed(session)
            session.commit()
        yield engine
    finally:
        engine.dispose()


def _load_mig_003(name: str):
    spec = importlib.util.spec_from_file_location(name, MIG_003_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _apply_mig_003(engine) -> None:
    module = _load_mig_003("mig_003")
    with engine.begin() as connection:
        context = MigrationContext.configure(connection)
        module.op = Operations(context)
        module.upgrade()


def _previous_schema_engine(tmp_path: Path):
    engine = create_sqlite_engine(tmp_path / "migration.db")
    with engine.begin() as connection:
        for table_name in PREVIOUS_TABLES:
            Base.metadata.tables[table_name].create(connection, checkfirst=True)
    _apply_mig_003(engine)
    return engine


def test_mig_003_applies_on_mig_002_shape_and_installs_exact_pv_triggers(
    tmp_path: Path,
) -> None:
    engine = _previous_schema_engine(tmp_path)
    try:
        names = set(inspect(engine).get_table_names())
        assert names == set(PREVIOUS_TABLES) | {
            "assessment_baselines",
            "baseline_members",
        }
        with engine.connect() as connection:
            triggers = dict(
                connection.execute(
                    text("SELECT name, sql FROM sqlite_master WHERE type='trigger'")
                ).all()
            )
            assert set(triggers) == {
                "trg_product_versions_baseline_update_immutable",
                "trg_product_versions_baseline_delete_immutable",
            }
            for sql in triggers.values():
                assert "bm.object_type = 'Product Version'" in sql
                assert "bm.object_id = OLD.product_version_id" in sql
            assert connection.execute(text("PRAGMA foreign_keys")).scalar_one() == 1
    finally:
        engine.dispose()


def test_mig_003_downgrade_removes_trigger_subset_and_baseline_tables(
    tmp_path: Path,
) -> None:
    engine = _previous_schema_engine(tmp_path)
    try:
        module = _load_mig_003("mig_003_down")
        with engine.begin() as connection:
            context = MigrationContext.configure(connection)
            module.op = Operations(context)
            module.downgrade()
        assert set(inspect(engine).get_table_names()) == set(PREVIOUS_TABLES)
        with engine.connect() as connection:
            trigger_count = connection.execute(
                text(
                    "SELECT COUNT(*) FROM sqlite_master "
                    "WHERE type='trigger' AND name LIKE 'trg_product_versions_baseline_%'"
                )
            ).scalar_one()
            assert trigger_count == 0
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    ("scenario", "baseline_id", "case_id", "prefix", "timestamp"),
    [
        ("A", "BL-A01", "CHG-A01", "BM-A01", "2026-08-25T19:10:00"),
        ("B", "BL-B01", "CHG-B01", "BM-B01", "2026-08-25T20:20:00"),
        ("C", "BL-C01", "CHG-C01", "BM-C01", "2026-08-25T21:40:00"),
    ],
)
def test_exact_frozen_baseline_member_sets_persist(
    engine,
    scenario: str,
    baseline_id: str,
    case_id: str,
    prefix: str,
    timestamp: str,
) -> None:
    with Session(engine) as session, session.begin():
        load_frozen_baseline_fixture(session, scenario)

    with Session(engine) as session:
        baseline = session.get(AssessmentBaseline, baseline_id)
        assert baseline is not None
        assert baseline.change_case_id == case_id
        assert baseline.configuration_context_id == "CFG-001"
        assert baseline.rule_set_version == "RRR-v0.1"
        assert baseline.snapshot_timestamp.isoformat().startswith(timestamp)
        assert baseline.effectivity_context == {
            "effectivity_type": "Planned Engineering Effective Date",
            "planned_effective_date": "2026-11-01",
        }
        members = list(
            session.scalars(
                select(BaselineMember)
                .where(BaselineMember.assessment_baseline_id == baseline_id)
                .order_by(BaselineMember.baseline_member_id)
            )
        )
        assert [member.baseline_member_id for member in members] == [
            f"{prefix}-{index:02d}" for index in range(1, 11)
        ]
        assert [(member.object_type, member.object_id) for member in members] == [
            ("Product Version", "PV-002"),
            ("Product Version", "PV-003"),
            ("Product Structure Occurrence", "PSO-002"),
            ("Configuration Context", "CFG-001"),
            ("Applicability Rule", "APP-001"),
            ("Effectivity Specification", "EFF-001"),
            ("Requirement", "REQ-001"),
            ("Requirement", "REQ-002"),
            ("Requirement", "REQ-003"),
            ("Requirement", "REQ-004"),
        ]
        assert [member.object_revision_or_state_token for member in members] == [
            "A.1",
            "A.1",
            "PSO-002@2026-08-25T18:00:00Z",
            "Complete@2026-08-25",
            "v1",
            "2026-11-01",
            "r1",
            "r1",
            "r1",
            "r1",
        ]
        assert [member.source_identifier for member in members] == [
            "PDS-PV-002-A1",
            "PDS-PV-003-A1",
            "PDS-PSO-002",
            "CFG-001",
            "APP-001",
            "EFF-001",
            "REQSRC-001",
            "REQSRC-002",
            "REQSRC-003",
            "REQSRC-004",
        ]
        canonical = read_canonical_baseline_snapshots()
        expected_by_identity = {
            (item.object_type, item.object_id): item.snapshot_payload
            for item in canonical.values()
        }
        for member in members:
            expected = expected_by_identity[(member.object_type, member.object_id)]
            if member.object_type == "Requirement":
                assert member.snapshot_payload["extraction_timestamp"].replace(
                    "+00:00", "Z"
                ) == expected["extraction_timestamp"]
                assert {
                    key: value
                    for key, value in member.snapshot_payload.items()
                    if key != "extraction_timestamp"
                } == {
                    key: value
                    for key, value in expected.items()
                    if key != "extraction_timestamp"
                }
            else:
                assert member.snapshot_payload == expected


def test_partial_baseline_creation_rolls_back(engine) -> None:
    baseline, members = frozen_baseline_inputs("A")
    duplicate = members[1].model_copy(
        update={"baseline_member_id": members[0].baseline_member_id}
    )
    bad_members = [members[0], duplicate, *members[2:]]

    with Session(engine) as session:
        with pytest.raises(IntegrityError):
            with session.begin():
                create_assessment_baseline(session, baseline, bad_members)

    with Session(engine) as session:
        assert session.get(AssessmentBaseline, "BL-A01") is None
        assert session.scalar(
            select(BaselineMember).where(
                BaselineMember.assessment_baseline_id == "BL-A01"
            )
        ) is None


def test_noncanonical_snapshot_is_rejected_before_persistence(engine) -> None:
    baseline, members = frozen_baseline_inputs("A")
    changed = dict(members[1].snapshot_payload)
    changed["material_characteristic"] = "MC-NOT-FROZEN"
    members[1] = members[1].model_copy(update={"snapshot_payload": changed})
    with Session(engine) as session:
        with pytest.raises(ValueError, match="frozen canonical snapshot"):
            with session.begin():
                create_assessment_baseline(session, baseline, members)
        assert session.get(AssessmentBaseline, "BL-A01") is None


def test_baseline_reuse_requires_all_five_inputs() -> None:
    all_true = BaselineReuseInputs(
        authoritative_current_state_unchanged=True,
        baseline_scope_still_sufficient=True,
        configuration_context_still_valid=True,
        effectivity_context_still_valid=True,
        extraction_basis_still_accepted=True,
    )
    assert baseline_reuse_permitted(all_true) is True
    for field in BaselineReuseInputs.model_fields:
        values = all_true.model_dump()
        values[field] = False
        assert baseline_reuse_permitted(BaselineReuseInputs(**values)) is False


def test_scenario_b_reuses_bl_b01_without_creating_a_second_baseline(engine) -> None:
    inputs = BaselineReuseInputs(
        authoritative_current_state_unchanged=True,
        baseline_scope_still_sufficient=True,
        configuration_context_still_valid=True,
        effectivity_context_still_valid=True,
        extraction_basis_still_accepted=True,
    )
    with Session(engine) as session, session.begin():
        original = load_frozen_baseline_fixture(session, "B")
        reused = reuse_assessment_baseline(
            session,
            "BL-B01",
            "CHG-B01",
            inputs,
        )
        assert reused is original
    with Session(engine) as session:
        ids = list(session.scalars(select(AssessmentBaseline.assessment_baseline_id)))
        assert ids == ["BL-B01"]


def test_source_is_baselined_flag_does_not_trigger_application_lock_before_capture(
    engine,
) -> None:
    with Session(engine) as session, session.begin():
        source = session.get(ProductVersion, "PV-003")
        assert source is not None and source.is_baselined is True
        assert is_product_version_captured_in_baseline(session, "PV-003") is False
        update_product_version_lifecycle_state(session, "PV-003", "Working Probe")
        assert source.lifecycle_state == "Working Probe"


def test_application_update_and_delete_fail_after_product_version_capture(engine) -> None:
    with Session(engine) as session, session.begin():
        load_frozen_baseline_fixture(session, "A")
    with Session(engine) as session:
        with pytest.raises(ImmutableRecordError):
            update_product_version_lifecycle_state(session, "PV-003", "Changed")
        session.rollback()
        with pytest.raises(ImmutableRecordError):
            delete_product_version(session, "PV-003")
        session.rollback()
        assert session.get(ProductVersion, "PV-003") is not None


def test_direct_sql_update_and_delete_fail_after_product_version_capture(
    tmp_path: Path,
) -> None:
    engine = _previous_schema_engine(tmp_path)
    try:
        with Session(engine) as session:
            _seed(session)
            session.commit()
            load_frozen_baseline_fixture(session, "A")
            session.commit()

        with engine.begin() as connection:
            with pytest.raises(
                IntegrityError,
                match="baselined Product Version is immutable",
            ):
                connection.execute(
                    text(
                        "UPDATE product_versions SET lifecycle_state='Changed' "
                        "WHERE product_version_id='PV-003'"
                    )
                )
        with engine.begin() as connection:
            with pytest.raises(
                IntegrityError,
                match="baselined Product Version is immutable",
            ):
                connection.execute(
                    text("DELETE FROM product_versions WHERE product_version_id='PV-003'")
                )
        with engine.connect() as connection:
            assert connection.execute(
                text(
                    "SELECT lifecycle_state FROM product_versions "
                    "WHERE product_version_id='PV-003'"
                )
            ).scalar_one() == "Current"
    finally:
        engine.dispose()


def test_product_version_trigger_scope_does_not_prevent_future_overlay_storage(
    tmp_path: Path,
) -> None:
    engine = _previous_schema_engine(tmp_path)
    try:
        with Session(engine) as session:
            _seed(session)
            session.commit()
            load_frozen_baseline_fixture(session, "A")
            session.commit()
        # INC-04 owns the real overlay tables. This technical probe proves the INC-03
        # triggers are scoped only to authoritative product_versions mutation.
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE TEMP TABLE overlay_successor_probe "
                    "(state_payload JSON NOT NULL)"
                )
            )
            connection.execute(
                text(
                    "INSERT INTO overlay_successor_probe(state_payload) VALUES (:payload)"
                ),
                {
                    "payload": (
                        '{"supersedes_product_version_id":"PV-003",'
                        '"proposed_revision":"B"}'
                    )
                },
            )
            assert connection.execute(
                text("SELECT COUNT(*) FROM overlay_successor_probe")
            ).scalar_one() == 1
            assert connection.execute(
                text(
                    "SELECT revision FROM product_versions "
                    "WHERE product_version_id='PV-003'"
                )
            ).scalar_one() == "A"
    finally:
        engine.dispose()
