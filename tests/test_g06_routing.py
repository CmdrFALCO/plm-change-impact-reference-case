from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from plm_ref.application.impact_analysis import execute_impact_analysis
from plm_ref.application.routing import route_impact_execution
from plm_ref.application.source_projection import load_shared_source_fixture
from plm_ref.domain.errors import RoutingEligibilityError
from plm_ref.infrastructure.db.models import (
    AssessmentObligation,
    BaselineMember,
    ChangeCase,
    ImpactCandidate,
    ImpactExecution,
    ProductStructureOccurrence,
)
from plm_ref.infrastructure.db.session import create_sqlite_engine
from plm_ref.infrastructure.impact.frozen_fixture_adapter import (
    FrozenFixtureImpactAdapter,
)
from plm_ref.rules.rrr_v01 import (
    RULE_SET_REGISTRY,
    RrrV01RuleSet,
    parse_bounded_applicability,
    supplier_related_trigger,
    validated_scope_relation,
)
from test_g05_impact_execution import (
    _add_b02_overlay,
    _b02_execution,
    _execute_frozen,
    _execution,
    _prepare_initial_scenario,
)


@pytest.fixture
def engine(tmp_path: Path):
    database_path = tmp_path / "g06.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{database_path}")
    command.upgrade(config, "mig_006")
    database_engine = create_sqlite_engine(database_path)
    try:
        with Session(database_engine) as session, session.begin():
            load_shared_source_fixture(session)
        yield database_engine
    finally:
        database_engine.dispose()


def test_mig_006_applies_complete_assessment_persistence_boundary(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "migration.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{database_path}")
    command.upgrade(config, "mig_006")
    database_engine = create_sqlite_engine(database_path)
    try:
        schema = inspect(database_engine)
        assert {
            "assessment_obligations",
            "assessments",
            "assessment_impact_links",
            "assessment_requirement_conclusions",
            "assessment_evidence_uses",
            "assessment_reuse_classifications",
        } <= set(schema.get_table_names())
        assert {
            constraint["name"]
            for constraint in schema.get_unique_constraints(
                "assessment_requirement_conclusions"
            )
        } == {"uq_assessment_requirement_conclusion"}
        assert {
            constraint["name"]
            for constraint in schema.get_unique_constraints(
                "assessment_reuse_classifications"
            )
        } == {"uq_assessment_reuse_target_execution"}
        with database_engine.connect() as connection:
            assert connection.exec_driver_sql(
                "SELECT version_num FROM alembic_version"
            ).scalar_one() == "mig_006"
    finally:
        database_engine.dispose()


def test_mig_006_downgrade_removes_only_assessment_boundary_tables(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "downgrade.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{database_path}")
    command.upgrade(config, "mig_006")
    command.downgrade(config, "mig_005")
    database_engine = create_sqlite_engine(database_path)
    try:
        tables = set(inspect(database_engine).get_table_names())
        assert "impact_executions" in tables
        assert not {
            "assessment_obligations",
            "assessments",
            "assessment_impact_links",
            "assessment_requirement_conclusions",
            "assessment_evidence_uses",
            "assessment_reuse_classifications",
        } & tables
        with database_engine.connect() as connection:
            assert connection.exec_driver_sql(
                "SELECT version_num FROM alembic_version"
            ).scalar_one() == "mig_005"
    finally:
        database_engine.dispose()


def _obligation_rows(session: Session, impact_execution_id: str) -> list[tuple]:
    return list(
        session.execute(
            select(
                AssessmentObligation.assessment_obligation_id,
                AssessmentObligation.impact_candidate_id,
                AssessmentObligation.domain,
                AssessmentObligation.requirement_id,
                AssessmentObligation.mandatory,
                AssessmentObligation.fulfilled_by_assessment_id,
                AssessmentObligation.routing_rule_reference,
            )
            .where(
                AssessmentObligation.impact_execution_id
                == impact_execution_id
            )
            .order_by(AssessmentObligation.assessment_obligation_id)
        )
    )


@pytest.mark.parametrize("scenario", ["A", "C"])
def test_initial_scenario_routing_matches_exact_frozen_oracle(
    engine, scenario: str
) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, scenario)
        _execute_frozen(session, _execution(scenario))
        execution = route_impact_execution(
            session, _execution(scenario).impact_execution_id
        )
        assert execution.routing_status == "Completed"

    with Session(engine) as session:
        prefix = scenario
        assert _obligation_rows(session, f"IAX-{prefix}01") == [
            (
                f"AO-{prefix}01",
                f"IC-{prefix}01",
                "Product Engineering",
                "REQ-001",
                True,
                None,
                "RRR-01",
            ),
            (
                f"AO-{prefix}02",
                f"IC-{prefix}02",
                "Validation",
                "REQ-002",
                True,
                None,
                "RRR-02",
            ),
            (
                f"AO-{prefix}03",
                f"IC-{prefix}03",
                "Manufacturing",
                "REQ-003",
                True,
                None,
                "RRR-03",
            ),
            (
                f"AO-{prefix}04",
                f"IC-{prefix}04",
                "Purchasing/Cost",
                None,
                True,
                None,
                "RRR-04",
            ),
        ]
        assert list(
            session.scalars(
                select(ImpactCandidate.candidate_state)
                .where(
                    ImpactCandidate.impact_execution_id == f"IAX-{prefix}01"
                )
                .order_by(ImpactCandidate.impact_candidate_id)
            )
        ) == ["Assessment Planned"] * 4


def test_b01_and_b02_routing_matches_exact_frozen_oracle_without_candidates(
    engine,
) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "B")
        _execute_frozen(session, _execution("B"))
        route_impact_execution(session, "IAX-B01")
        _add_b02_overlay(session)
        _execute_frozen(session, _b02_execution())
        route_impact_execution(session, "IAX-B02")

    with Session(engine) as session:
        assert _obligation_rows(session, "IAX-B01") == [
            ("AO-B01", "IC-B01", "Product Engineering", "REQ-004", True, None, "RRR-01"),
            ("AO-B02", "IC-B02", "Validation", "REQ-002", True, None, "RRR-02"),
            ("AO-B03", "IC-B03", "Manufacturing", "REQ-003", True, None, "RRR-03"),
            ("AO-B04", "IC-B04", "Purchasing/Cost", None, True, None, "RRR-04"),
        ]
        assert _obligation_rows(session, "IAX-B02") == [
            ("AO-B21", "IC-B21", "Product Engineering", "REQ-004", True, None, "RRR-01"),
            ("AO-B22", "IC-B22", "Manufacturing", "REQ-003", True, None, "RRR-03"),
            ("AO-B23", None, "Validation", "REQ-002", True, None, "RRR-02"),
            ("AO-B24", None, "Purchasing/Cost", None, True, None, "RRR-04"),
        ]
        assert list(
            session.execute(
                select(
                    ImpactExecution.impact_execution_id,
                    ImpactExecution.routing_status,
                ).order_by(ImpactExecution.impact_execution_id)
            )
        ) == [("IAX-B01", "Completed"), ("IAX-B02", "Completed")]
        assert list(
            session.execute(
                select(
                    ImpactCandidate.impact_candidate_id,
                    ImpactCandidate.candidate_state,
                ).order_by(ImpactCandidate.impact_candidate_id)
            )
        ) == [
            ("IC-B01", "Assessment Planned"),
            ("IC-B02", "Assessment Planned"),
            ("IC-B03", "Assessment Planned"),
            ("IC-B04", "Assessment Planned"),
            ("IC-B21", "Assessment Planned"),
            ("IC-B22", "Assessment Planned"),
        ]


def test_rule_registry_has_exactly_the_frozen_binding() -> None:
    assert list(RULE_SET_REGISTRY) == ["RRR-v0.1"]
    assert isinstance(RULE_SET_REGISTRY["RRR-v0.1"], RrrV01RuleSet)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ('CoolingType = "Liquid"', frozenset({("CoolingType", "Liquid")})),
        (
            'PackFamily = "LongRange" AND CoolingType = "Liquid"',
            frozenset(
                {("CoolingType", "Liquid"), ("PackFamily", "LongRange")}
            ),
        ),
        ('CoolingType="Liquid"', frozenset({("CoolingType", "Liquid")})),
        ('CoolingType = "Liquid" OR PackFamily = "LongRange"', None),
        ('CoolingType = Liquid', None),
        ('(CoolingType = "Liquid")', None),
        ('CoolingType = "Liquid" and PackFamily = "LongRange"', None),
    ],
)
def test_bounded_applicability_parser_accepts_only_frozen_grammar(
    expression: str, expected: frozenset[tuple[str, str]] | None
) -> None:
    assert parse_bounded_applicability(expression) == expected


def test_bounded_applicability_relation_is_unordered_and_closed() -> None:
    assert validated_scope_relation(
        'CoolingType = "Liquid" AND PackFamily = "LongRange"',
        'PackFamily = "LongRange" AND CoolingType = "Liquid"',
    ) == "Equal"
    assert validated_scope_relation(
        'CoolingType = "Liquid" AND PackFamily = "LongRange"',
        'CoolingType = "Liquid"',
    ) == "Proposed Narrower"
    assert validated_scope_relation(
        'CoolingType = "Liquid"',
        'CoolingType = "Liquid" AND PackFamily = "LongRange"',
    ) == "Not Determinable"
    assert validated_scope_relation(
        'CoolingType = "Liquid" OR PackFamily = "LongRange"',
        'CoolingType = "Liquid"',
    ) == "Not Determinable"


def test_supplier_trigger_matching_is_exact_string_only() -> None:
    assert supplier_related_trigger("Synthetic supplier process change")
    assert supplier_related_trigger(
        "Synthetic supplier process change with elevated authority classification"
    )
    assert not supplier_related_trigger("synthetic supplier process change")
    assert not supplier_related_trigger("Synthetic supplier process change ")
    assert not supplier_related_trigger("Synthetic supplier process change detected")


def test_routing_does_not_read_later_live_product_source_state(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        _execute_frozen(session, _execution("A"))
        live_occurrence = session.get(ProductStructureOccurrence, "PSO-002")
        assert live_occurrence is not None
        live_occurrence.applicability_rule = {
            "rule_id": "LIVE-LATER",
            "expression": 'CoolingType = "Air" OR Unsupported = "True"',
            "rule_version": "99",
        }
        route_impact_execution(session, "IAX-A01")

    with Session(engine) as session:
        assert _obligation_rows(session, "IAX-A01")[0][3] == "REQ-001"
        assert session.get(ImpactExecution, "IAX-A01").routing_status == "Completed"


@pytest.mark.parametrize("failure", ["malformed-applicability", "missing-requirement"])
def test_missing_or_malformed_mandatory_input_fails_without_partial_routing(
    engine, failure: str
) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        if failure == "malformed-applicability":
            occurrence = session.get(BaselineMember, "BM-A01-03")
            assert occurrence is not None
            payload = deepcopy(occurrence.snapshot_payload)
            payload["applicability_rule"]["expression"] = (
                'CoolingType = "Liquid" OR PackFamily = "LongRange"'
            )
            occurrence.snapshot_payload = payload
        else:
            requirement = session.get(BaselineMember, "BM-A01-08")
            assert requirement is not None
            session.delete(requirement)
        _execute_frozen(session, _execution("A"))
        execution = route_impact_execution(session, "IAX-A01")
        assert execution.routing_status == "Failed"

    with Session(engine) as session:
        assert _obligation_rows(session, "IAX-A01") == []
        assert list(
            session.scalars(
                select(ImpactCandidate.candidate_state)
                .where(ImpactCandidate.impact_execution_id == "IAX-A01")
                .order_by(ImpactCandidate.impact_candidate_id)
            )
        ) == ["New"] * 4


def test_unknown_rule_set_fails_closed_without_partial_routing(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        _execute_frozen(session, _execution("A"))
        execution = session.get(ImpactExecution, "IAX-A01")
        assert execution is not None
        execution.rule_set_version = "RRR-v9.9"
        result = route_impact_execution(session, "IAX-A01")
        assert result.routing_status == "Failed"

    with Session(engine) as session:
        assert _obligation_rows(session, "IAX-A01") == []
        assert set(
            session.scalars(
                select(ImpactCandidate.candidate_state).where(
                    ImpactCandidate.impact_execution_id == "IAX-A01"
                )
            )
        ) == {"New"}


def test_routing_persistence_failure_rolls_back_all_new_positive_results(
    engine,
) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        _prepare_initial_scenario(session, "C")
        _execute_frozen(session, _execution("A"))
        _execute_frozen(session, _execution("C"))
        session.add(
            AssessmentObligation(
                assessment_obligation_id="AO-A03",
                impact_execution_id="IAX-C01",
                impact_candidate_id="IC-C01",
                domain="Product Engineering",
                requirement_id="REQ-001",
                mandatory=True,
                fulfilled_by_assessment_id=None,
                routing_rule_reference="RRR-01",
            )
        )
        session.flush()
        result = route_impact_execution(session, "IAX-A01")
        assert result.routing_status == "Failed"

    with Session(engine) as session:
        assert _obligation_rows(session, "IAX-A01") == []
        assert list(
            session.scalars(
                select(ImpactCandidate.candidate_state)
                .where(ImpactCandidate.impact_execution_id == "IAX-A01")
                .order_by(ImpactCandidate.impact_candidate_id)
            )
        ) == ["New"] * 4
        assert session.get(AssessmentObligation, "AO-A03").impact_execution_id == (
            "IAX-C01"
        )


def test_near_match_supplier_trigger_creates_no_purchasing_obligation(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        change_case = session.get(ChangeCase, "CHG-A01")
        assert change_case is not None
        change_case.trigger = "Synthetic supplier process change "
        _execute_frozen(session, _execution("A"))
        route_impact_execution(session, "IAX-A01")

    with Session(engine) as session:
        assert [row[2] for row in _obligation_rows(session, "IAX-A01")] == [
            "Product Engineering",
            "Validation",
            "Manufacturing",
        ]
        purchasing = session.get(ImpactCandidate, "IC-A04")
        assert purchasing is not None
        assert purchasing.candidate_state == "New"


def test_routing_cannot_start_before_impact_execution_completion(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        session.add(
            ImpactExecution(
                impact_execution_id="IAX-NOT-COMPLETE",
                change_case_id="CHG-A01",
                assessment_baseline_id="BL-A01",
                overlay_revision_id="OV-A01",
                rule_set_version="RRR-v0.1",
                execution_timestamp=_execution("A").execution_timestamp,
                execution_status="Running",
                routing_status="Not Started",
            )
        )
        session.flush()
        with pytest.raises(RoutingEligibilityError):
            route_impact_execution(session, "IAX-NOT-COMPLETE")
        assert session.get(
            ImpactExecution, "IAX-NOT-COMPLETE"
        ).routing_status == "Not Started"
