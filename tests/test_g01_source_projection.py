from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from plm_ref.application.source_projection import (
    DEFAULT_SHARED_SOURCE_FIXTURE,
    load_shared_source_fixture,
    read_shared_source_fixture,
)
from plm_ref.infrastructure.db.models import (
    ConfigurationContext,
    EvidenceRecord,
    ProductElement,
    ProductStructureOccurrence,
    ProductVersion,
    Requirement,
)
from plm_ref.infrastructure.db.session import create_sqlite_engine


EXPECTED_SOURCE_TABLES = {
    "product_elements",
    "product_versions",
    "product_structure_occurrences",
    "configuration_contexts",
    "requirements",
    "evidence_records",
}


def _upgrade_mig_001(database_path: Path) -> None:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{database_path}")
    command.upgrade(config, "head")


def _migrated_engine(tmp_path: Path):
    database_path = tmp_path / "g01.db"
    _upgrade_mig_001(database_path)
    return create_sqlite_engine(database_path)


def test_mig_001_applies_from_empty_database_and_creates_only_source_projection_tables(
    tmp_path: Path,
) -> None:
    engine = _migrated_engine(tmp_path)
    try:
        table_names = set(inspect(engine).get_table_names())
        assert table_names == EXPECTED_SOURCE_TABLES | {"alembic_version"}
        with engine.connect() as connection:
            assert connection.execute(text("PRAGMA foreign_keys")).scalar_one() == 1
    finally:
        engine.dispose()


def test_shared_source_fixture_validates_and_loads_exact_frozen_identities(tmp_path: Path) -> None:
    fixture = read_shared_source_fixture(DEFAULT_SHARED_SOURCE_FIXTURE)
    assert [item.rule_id for item in fixture.applicability_rules] == ["APP-001"]
    assert [
        item.effectivity_specification_id for item in fixture.effectivity_specifications
    ] == ["EFF-001"]

    engine = _migrated_engine(tmp_path)
    try:
        with Session(engine) as session, session.begin():
            result = load_shared_source_fixture(session)
            assert result.product_elements == 2
            assert result.product_versions == 2
            assert result.product_structure_occurrences == 1
            assert result.configuration_contexts == 1
            assert result.requirements == 4
            assert result.evidence_records == 4

        with Session(engine) as session:
            assert set(session.scalars(select(ProductElement.product_element_id))) == {
                "PE-002",
                "PE-003",
            }
            assert set(session.scalars(select(ProductVersion.product_version_id))) == {
                "PV-002",
                "PV-003",
            }
            assert set(session.scalars(select(ProductStructureOccurrence.occurrence_id))) == {
                "PSO-002"
            }
            assert set(
                session.scalars(select(ConfigurationContext.configuration_context_id))
            ) == {"CFG-001"}
            assert set(session.scalars(select(Requirement.requirement_id))) == {
                "REQ-001",
                "REQ-002",
                "REQ-003",
                "REQ-004",
            }
            assert set(session.scalars(select(EvidenceRecord.evidence_record_id))) == {
                "EV-001",
                "EV-002",
                "EV-003",
                "EV-004",
            }

            occurrence = session.get(ProductStructureOccurrence, "PSO-002")
            assert occurrence is not None
            assert occurrence.parent_product_version_id == "PV-002"
            assert occurrence.child_product_version_id == "PV-003"
            assert occurrence.position == "020"
            assert occurrence.quantity == 1
            assert occurrence.unit == "EA"
            assert occurrence.applicability_rule == {
                "rule_id": "APP-001",
                "expression": 'CoolingType = "Liquid"',
                "rule_version": "1",
            }
            assert occurrence.effectivity_specification == {
                "effectivity_type": "Planned Engineering Effective Date",
                "planned_effective_date": "2026-11-01",
            }

            context = session.get(ConfigurationContext, "CFG-001")
            assert context is not None
            assert context.feature_values == {
                "PackFamily": "LongRange",
                "CoolingType": "Liquid",
            }
            assert context.completeness_state == "Complete"
    finally:
        engine.dispose()


def test_duplicate_product_version_element_revision_iteration_is_rejected(tmp_path: Path) -> None:
    engine = _migrated_engine(tmp_path)
    try:
        with Session(engine) as session, session.begin():
            load_shared_source_fixture(session)

        with Session(engine) as session:
            session.add(
                ProductVersion(
                    product_version_id="PV-DUP",
                    product_element_id="PE-003",
                    revision="A",
                    iteration="1",
                    lifecycle_state="Current",
                    is_baselined=False,
                    supersedes_product_version_id=None,
                    source_class="Product Data Source",
                    source_identifier="PDS-PV-DUP",
                    extraction_timestamp=datetime(2026, 8, 25, 18, 0, tzinfo=timezone.utc),
                )
            )
            with pytest.raises(IntegrityError):
                session.commit()
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    ("parent_id", "child_id"),
    [
        ("PV-MISSING", "PV-003"),
        ("PV-002", "PV-MISSING"),
    ],
)
def test_invalid_occurrence_product_version_reference_is_rejected(
    tmp_path: Path, parent_id: str, child_id: str
) -> None:
    engine = _migrated_engine(tmp_path)
    try:
        with Session(engine) as session, session.begin():
            load_shared_source_fixture(session)

        with Session(engine) as session:
            session.add(
                ProductStructureOccurrence(
                    occurrence_id=f"PSO-BAD-{parent_id}-{child_id}",
                    parent_product_version_id=parent_id,
                    child_product_version_id=child_id,
                    position="999",
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
                    source_identifier="PDS-PSO-BAD",
                    extraction_timestamp=datetime(2026, 8, 25, 18, 0, tzinfo=timezone.utc),
                )
            )
            with pytest.raises(IntegrityError):
                session.commit()
    finally:
        engine.dispose()


def test_foreign_keys_remain_enabled_on_repeated_application_connections(tmp_path: Path) -> None:
    engine = _migrated_engine(tmp_path)
    try:
        for _ in range(3):
            with engine.connect() as connection:
                assert connection.execute(text("PRAGMA foreign_keys")).scalar_one() == 1
    finally:
        engine.dispose()
