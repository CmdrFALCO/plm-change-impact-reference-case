from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from plm_ref.application.baseline import load_frozen_baseline_fixture
from plm_ref.application.change_case import (
    ChangeCaseInput,
    ChangeItemRevisionInput,
    ProposalStateInput,
    create_change_case,
    create_change_item,
)
from plm_ref.application.impact_analysis import (
    ImpactExecutionInput,
    execute_impact_analysis,
    validate_execution_lineage,
)
from plm_ref.application.overlay import OverlayRevisionInput, create_overlay_revision
from plm_ref.application.source_projection import load_shared_source_fixture
from plm_ref.domain.errors import ImpactExecutionLineageError, ImmutableRecordError
from plm_ref.infrastructure.db.guards import (
    assert_assessment_baseline_mutable,
    assert_baseline_members_mutable,
    assert_overlay_local_objects_mutable,
    assert_overlay_memberships_mutable,
    assert_overlay_revision_mutable,
)
from plm_ref.infrastructure.db.models import (
    ImpactCandidate,
    ImpactCandidatePathStep,
    ImpactCandidateProvenance,
    ImpactExecution,
)
from plm_ref.infrastructure.db.session import create_sqlite_engine
from plm_ref.infrastructure.impact.frozen_fixture_adapter import (
    FrozenFixtureImpactAdapter,
)


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
        "execution_id": "IAX-A01",
        "case_created_at": "2026-08-25T19:00:00Z",
        "revision_created_at": "2026-08-25T19:02:00Z",
        "proposal_changed_at": "2026-08-25T19:03:00Z",
        "overlay_created_at": "2026-08-25T19:20:00Z",
        "execution_timestamp": "2026-08-25T19:25:00Z",
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
        "execution_id": "IAX-B01",
        "case_created_at": "2026-08-25T20:10:00Z",
        "revision_created_at": "2026-08-25T20:12:00Z",
        "proposal_changed_at": "2026-08-25T20:13:00Z",
        "overlay_created_at": "2026-08-25T20:30:00Z",
        "execution_timestamp": "2026-08-25T20:35:00Z",
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
        "execution_id": "IAX-C01",
        "case_created_at": "2026-08-25T21:30:00Z",
        "revision_created_at": "2026-08-25T21:32:00Z",
        "proposal_changed_at": "2026-08-25T21:33:00Z",
        "overlay_created_at": "2026-08-25T21:50:00Z",
        "execution_timestamp": "2026-08-25T21:55:00Z",
        "owner": "Change Owner C",
        "material": "MC-C-01",
        "scope": 'CoolingType = "Liquid"',
        "trigger": (
            "Synthetic supplier process change with elevated authority "
            "classification"
        ),
    },
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
        created_at=_dt(values["case_created_at"]),
        closed_at=None,
    )


def _revise(scenario: str) -> ChangeItemRevisionInput:
    values = SCENARIOS[scenario]
    return ChangeItemRevisionInput(
        change_item_id=values["item_id"],
        change_item_revision="r1",
        change_case_id=values["case_id"],
        action="Revise Product State",
        target_type="Product Version",
        target_id="PV-003",
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


def _proposal(scenario: str, item_id: str | None = None) -> ProposalStateInput:
    values = SCENARIOS[scenario]
    return ProposalStateInput(
        change_item_id=item_id or values["item_id"],
        change_case_id=values["case_id"],
        selected_revision="r1",
        proposal_state="Active",
        state_changed_at=_dt(values["proposal_changed_at"]),
        state_changed_by=values["owner"],
    )


def _applicability() -> ChangeItemRevisionInput:
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


def _prepare_initial_scenario(session: Session, scenario: str) -> None:
    values = SCENARIOS[scenario]
    create_change_case(session, _case(scenario))
    create_change_item(session, _revise(scenario), _proposal(scenario))
    load_frozen_baseline_fixture(session, scenario)
    create_overlay_revision(
        session,
        values["baseline_id"],
        OverlayRevisionInput(
            overlay_revision_id=values["overlay_id"],
            change_case_id=values["case_id"],
            created_at=_dt(values["overlay_created_at"]),
        ),
    )


def _add_b02_overlay(session: Session) -> None:
    create_change_item(session, _applicability(), _proposal("B", "CI-B02"))
    create_overlay_revision(
        session,
        "BL-B01",
        OverlayRevisionInput(
            overlay_revision_id="OV-B02",
            change_case_id="CHG-B01",
            created_at=_dt("2026-08-25T21:10:00Z"),
        ),
        local_object_ids={
            "CI-B01": "OVOBJ-B02-PV",
            "CI-B02": "OVOBJ-B02-PSO",
        },
    )


def _execution(scenario: str, **overrides: str) -> ImpactExecutionInput:
    values = SCENARIOS[scenario]
    raw = {
        "impact_execution_id": values["execution_id"],
        "change_case_id": values["case_id"],
        "assessment_baseline_id": values["baseline_id"],
        "overlay_revision_id": values["overlay_id"],
        "rule_set_version": "RRR-v0.1",
        "execution_timestamp": _dt(values["execution_timestamp"]),
    }
    raw.update(overrides)
    return ImpactExecutionInput.model_validate(raw)


def _b02_execution() -> ImpactExecutionInput:
    return ImpactExecutionInput(
        impact_execution_id="IAX-B02",
        change_case_id="CHG-B01",
        assessment_baseline_id="BL-B01",
        overlay_revision_id="OV-B02",
        rule_set_version="RRR-v0.1",
        execution_timestamp=_dt("2026-08-25T21:15:00Z"),
    )


@pytest.fixture
def engine(tmp_path: Path):
    database_path = tmp_path / "g05.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{database_path}")
    command.upgrade(config, "mig_005")
    database_engine = create_sqlite_engine(database_path)
    try:
        with Session(database_engine) as session, session.begin():
            load_shared_source_fixture(session)
        yield database_engine
    finally:
        database_engine.dispose()


def test_mig_005_applies_bounded_tables_constraints_and_first_use_triggers(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "migration.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{database_path}")
    command.upgrade(config, "mig_005")
    database_engine = create_sqlite_engine(database_path)
    try:
        schema = inspect(database_engine)
        assert {
            "impact_executions",
            "impact_candidates",
            "impact_candidate_provenance",
            "impact_candidate_path_steps",
        } <= set(schema.get_table_names())
        assert {
            column["name"] for column in schema.get_columns("impact_executions")
        } == {
            "impact_execution_id",
            "change_case_id",
            "assessment_baseline_id",
            "overlay_revision_id",
            "rule_set_version",
            "execution_timestamp",
            "execution_status",
            "routing_status",
        }
        with database_engine.connect() as connection:
            triggers = set(
                connection.scalars(
                    text(
                        "SELECT name FROM sqlite_master WHERE type='trigger' "
                        "AND (name LIKE 'trg_assessment_baselines_execution_%' "
                        "OR name LIKE 'trg_baseline_members_execution_%' "
                        "OR name LIKE 'trg_overlay_%_execution_%')"
                    )
                )
            )
            assert len(triggers) == 13
            assert connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one() == "mig_005"
    finally:
        database_engine.dispose()


def test_mig_005_downgrade_removes_impact_tables_and_first_use_triggers(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "downgrade.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{database_path}")
    command.upgrade(config, "mig_005")
    command.downgrade(config, "mig_004")
    database_engine = create_sqlite_engine(database_path)
    try:
        assert not {
            "impact_executions",
            "impact_candidates",
            "impact_candidate_provenance",
            "impact_candidate_path_steps",
        } & set(inspect(database_engine).get_table_names())
        with database_engine.connect() as connection:
            assert connection.execute(
                text(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='trigger' "
                    "AND (name LIKE '%_execution_%')"
                )
            ).scalar_one() == 0
            assert connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one() == "mig_004"
    finally:
        database_engine.dispose()


def _execute_frozen(session: Session, command_input: ImpactExecutionInput) -> None:
    execution = execute_impact_analysis(
        session, command_input, FrozenFixtureImpactAdapter()
    )
    assert execution.execution_status == "Completed"
    assert execution.routing_status == "Not Started"


@pytest.mark.parametrize("scenario", ["A", "C"])
def test_exact_initial_frozen_execution_candidates_and_provenance(
    engine, scenario: str
) -> None:
    values = SCENARIOS[scenario]
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, scenario)
        _execute_frozen(session, _execution(scenario))

    prefix = scenario
    with Session(engine) as session:
        execution = session.get(ImpactExecution, values["execution_id"])
        assert execution is not None
        assert _utc_token(execution.execution_timestamp) == values[
            "execution_timestamp"
        ]
        assert (execution.execution_status, execution.routing_status) == (
            "Completed",
            "Not Started",
        )
        assert list(
            session.execute(
                select(
                    ImpactCandidate.impact_candidate_id,
                    ImpactCandidate.candidate_type,
                    ImpactCandidate.candidate_reference,
                    ImpactCandidate.affected_domain,
                    ImpactCandidate.candidate_state,
                )
                .where(
                    ImpactCandidate.impact_execution_id
                    == values["execution_id"]
                )
                .order_by(ImpactCandidate.impact_candidate_id)
            )
        ) == [
            (
                f"IC-{prefix}01",
                "Product Structure Occurrence",
                "PSO-002",
                "Product Engineering",
                "New",
            ),
            (f"IC-{prefix}02", "Product Version", "PV-003", "Validation", "New"),
            (
                f"IC-{prefix}03",
                "Product Structure Occurrence",
                "PSO-002",
                "Manufacturing",
                "New",
            ),
            (
                f"IC-{prefix}04",
                "Product Version",
                "PV-003",
                "Purchasing/Cost",
                "New",
            ),
        ]
        assert list(
            session.execute(
                select(
                    ImpactCandidateProvenance.impact_candidate_provenance_id,
                    ImpactCandidateProvenance.impact_candidate_id,
                    ImpactCandidateProvenance.change_item_id,
                    ImpactCandidateProvenance.change_item_revision,
                ).order_by(
                    ImpactCandidateProvenance.impact_candidate_provenance_id
                )
            )
        ) == [
            (f"ICP-{prefix}0{number}", f"IC-{prefix}0{number}", f"CI-{prefix}01", "r1")
            for number in range(1, 5)
        ]
        steps = list(
            session.execute(
                select(
                    ImpactCandidatePathStep.impact_candidate_provenance_id,
                    ImpactCandidatePathStep.sequence,
                    ImpactCandidatePathStep.source_reference,
                    ImpactCandidatePathStep.relationship_type,
                    ImpactCandidatePathStep.target_reference,
                    ImpactCandidatePathStep.state_context,
                ).order_by(
                    ImpactCandidatePathStep.impact_candidate_provenance_id,
                    ImpactCandidatePathStep.sequence,
                )
            )
        )
        assert steps == [
            (
                f"ICP-{prefix}01",
                1,
                f"BM-{prefix}01-02",
                "REFERENCED_BY_OCCURRENCE",
                f"BM-{prefix}01-03",
                "Current State",
            ),
            (
                f"ICP-{prefix}01",
                2,
                f"BM-{prefix}01-03",
                "OCCURS_IN_PARENT",
                f"BM-{prefix}01-01",
                "Current State",
            ),
            (
                f"ICP-{prefix}02",
                1,
                f"BM-{prefix}01-02",
                "REFERENCED_BY_OCCURRENCE",
                f"BM-{prefix}01-03",
                "Current State",
            ),
            (
                f"ICP-{prefix}03",
                1,
                f"BM-{prefix}01-02",
                "REFERENCED_BY_OCCURRENCE",
                f"BM-{prefix}01-03",
                "Current State",
            ),
            (
                f"ICP-{prefix}03",
                2,
                f"BM-{prefix}01-03",
                "OCCURS_IN_PARENT",
                f"BM-{prefix}01-01",
                "Current State",
            ),
            (
                f"ICP-{prefix}04",
                1,
                f"BM-{prefix}01-02",
                "REFERENCED_BY_OCCURRENCE",
                f"BM-{prefix}01-03",
                "Current State",
            ),
        ]


def test_b01_then_b02_persists_only_the_frozen_second_execution_delta(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "B")
        _execute_frozen(session, _execution("B"))
        _add_b02_overlay(session)
        _execute_frozen(session, _b02_execution())

    with Session(engine) as session:
        b01 = session.get(ImpactExecution, "IAX-B01")
        b02 = session.get(ImpactExecution, "IAX-B02")
        assert b01 is not None and b02 is not None
        assert _utc_token(b01.execution_timestamp) == "2026-08-25T20:35:00Z"
        assert _utc_token(b02.execution_timestamp) == "2026-08-25T21:15:00Z"
        assert (b02.execution_status, b02.routing_status) == (
            "Completed",
            "Not Started",
        )
        assert list(
            session.execute(
                select(
                    ImpactCandidate.impact_candidate_id,
                    ImpactCandidate.candidate_type,
                    ImpactCandidate.candidate_reference,
                    ImpactCandidate.affected_domain,
                    ImpactCandidate.candidate_state,
                )
                .where(ImpactCandidate.impact_execution_id == "IAX-B01")
                .order_by(ImpactCandidate.impact_candidate_id)
            )
        ) == [
            ("IC-B01", "Product Structure Occurrence", "PSO-002", "Product Engineering", "New"),
            ("IC-B02", "Product Version", "PV-003", "Validation", "New"),
            ("IC-B03", "Product Structure Occurrence", "PSO-002", "Manufacturing", "New"),
            ("IC-B04", "Product Version", "PV-003", "Purchasing/Cost", "New"),
        ]
        assert list(
            session.execute(
                select(
                    ImpactCandidate.impact_candidate_id,
                    ImpactCandidate.candidate_type,
                    ImpactCandidate.candidate_reference,
                    ImpactCandidate.affected_domain,
                    ImpactCandidate.candidate_state,
                )
                .where(ImpactCandidate.impact_execution_id == "IAX-B02")
                .order_by(ImpactCandidate.impact_candidate_id)
            )
        ) == [
            (
                "IC-B21",
                "Product Structure Occurrence",
                "OVOBJ-B02-PSO",
                "Product Engineering",
                "New",
            ),
            ("IC-B22", "Product Structure Occurrence", "OVOBJ-B02-PSO", "Manufacturing", "New"),
        ]
        b02_provenance = list(
            session.execute(
                select(
                    ImpactCandidateProvenance.impact_candidate_provenance_id,
                    ImpactCandidateProvenance.impact_candidate_id,
                    ImpactCandidateProvenance.change_item_id,
                    ImpactCandidateProvenance.change_item_revision,
                )
                .join(
                    ImpactCandidate,
                    ImpactCandidate.impact_candidate_id
                    == ImpactCandidateProvenance.impact_candidate_id,
                )
                .where(ImpactCandidate.impact_execution_id == "IAX-B02")
                .order_by(
                    ImpactCandidateProvenance.impact_candidate_provenance_id
                )
            )
        )
        assert b02_provenance == [
            ("ICP-B21", "IC-B21", "CI-B02", "r1"),
            ("ICP-B22", "IC-B22", "CI-B02", "r1"),
        ]
        assert list(
            session.execute(
                select(
                    ImpactCandidatePathStep.impact_candidate_provenance_id,
                    ImpactCandidatePathStep.sequence,
                    ImpactCandidatePathStep.source_reference,
                    ImpactCandidatePathStep.relationship_type,
                    ImpactCandidatePathStep.target_reference,
                    ImpactCandidatePathStep.state_context,
                )
                .where(
                    ImpactCandidatePathStep.impact_candidate_provenance_id.in_(
                        ["ICP-B21", "ICP-B22"]
                    )
                )
                .order_by(
                    ImpactCandidatePathStep.impact_candidate_provenance_id
                )
            )
        ) == [
            (
                "ICP-B21",
                1,
                "OVOBJ-B02-PV",
                "REFERENCED_BY_OCCURRENCE",
                "OVOBJ-B02-PSO",
                "Proposed State",
            ),
            (
                "ICP-B22",
                1,
                "OVOBJ-B02-PV",
                "REFERENCED_BY_OCCURRENCE",
                "OVOBJ-B02-PSO",
                "Proposed State",
            ),
        ]


class _StaticAdapter:
    def __init__(self, candidates: object) -> None:
        self.candidates = candidates

    def run(self, _context):  # type: ignore[no-untyped-def]
        return self.candidates


def _fixture_candidate_dict(session: Session) -> dict:
    adapter = FrozenFixtureImpactAdapter()
    command_input = _execution("A")
    context = validate_execution_lineage(session, command_input)
    return adapter.run(context)[0].model_dump()


@pytest.mark.parametrize(
    "malformation",
    [
        "noncontiguous",
        "disconnected",
        "wrong-current-reference",
        "wrong-proposed-reference",
        "cross-item",
    ],
)
def test_malformed_or_cross_case_provenance_fails_without_partial_results(
    engine, malformation: str
) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        if malformation in {"cross-item", "wrong-proposed-reference"}:
            _prepare_initial_scenario(session, "C")
        candidate = _fixture_candidate_dict(session)
        candidate["impact_candidate_id"] = f"IC-INVALID-{malformation}"
        provenance = candidate["provenance"][0]
        provenance["impact_candidate_provenance_id"] = (
            f"ICP-INVALID-{malformation}"
        )
        steps = provenance["dependency_path"]
        if malformation == "noncontiguous":
            steps[1]["sequence"] = 3
        elif malformation == "disconnected":
            steps[1]["source_reference"] = "BM-A01-02"
        elif malformation == "wrong-current-reference":
            steps[0]["source_reference"] = "BM-B01-02"
        elif malformation == "wrong-proposed-reference":
            steps[0]["state_context"] = "Proposed State"
            steps[0]["source_reference"] = "OVOBJ-C01-PV"
            steps[0]["target_reference"] = "OVOBJ-A01-PV"
            provenance["dependency_path"] = steps[:1]
        else:
            provenance["change_item_id"] = "CI-C01"

        command_input = _execution(
            "A", impact_execution_id=f"IAX-INVALID-{malformation}"
        )
        result = execute_impact_analysis(
            session, command_input, _StaticAdapter([candidate])
        )
        assert result.execution_status == "Failed"
        assert result.routing_status == "Not Started"

    with Session(engine) as session:
        execution_id = f"IAX-INVALID-{malformation}"
        assert session.scalar(
            select(ImpactCandidate).where(
                ImpactCandidate.impact_execution_id == execution_id
            )
        ) is None
        assert session.scalar(select(ImpactCandidateProvenance)) is None
        assert session.scalar(select(ImpactCandidatePathStep)) is None


@pytest.mark.parametrize("collision", ["candidate", "provenance"])
def test_candidate_and_provenance_ids_cannot_cross_execution_boundaries(
    engine, collision: str
) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        candidate = _fixture_candidate_dict(session)
        _execute_frozen(session, _execution("A"))
        if collision == "provenance":
            candidate["impact_candidate_id"] = "IC-CROSS-EXECUTION"
        result = execute_impact_analysis(
            session,
            _execution("A", impact_execution_id=f"IAX-CROSS-{collision}"),
            _StaticAdapter([candidate]),
        )
        assert result.execution_status == "Failed"

    with Session(engine) as session:
        assert session.scalar(
            select(ImpactCandidate).where(
                ImpactCandidate.impact_execution_id == f"IAX-CROSS-{collision}"
            )
        ) is None


def test_invalid_second_candidate_rolls_back_the_complete_result_set(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        first = _fixture_candidate_dict(session)
        second = _fixture_candidate_dict(session)
        second["impact_candidate_id"] = "IC-ATOMIC-02"
        second["provenance"][0]["impact_candidate_provenance_id"] = "ICP-ATOMIC-02"
        second["provenance"][0]["dependency_path"][0][
            "source_reference"
        ] = "BM-C01-02"
        execution = execute_impact_analysis(
            session,
            _execution("A", impact_execution_id="IAX-ATOMIC-FAIL"),
            _StaticAdapter([first, second]),
        )
        assert execution.execution_status == "Failed"

    with Session(engine) as session:
        assert session.scalar(select(ImpactCandidate)) is None
        assert session.scalar(select(ImpactCandidateProvenance)) is None
        assert session.scalar(select(ImpactCandidatePathStep)) is None


def test_cross_case_execution_lineage_fails_closed_before_adapter_use(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        _prepare_initial_scenario(session, "C")
        with pytest.raises(ImpactExecutionLineageError):
            execute_impact_analysis(
                session,
                _execution("A", assessment_baseline_id="BL-C01"),
                FrozenFixtureImpactAdapter(),
            )
        assert session.get(ImpactExecution, "IAX-A01") is None


def test_first_execution_use_is_guarded_at_application_layer(engine) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        _execute_frozen(session, _execution("A"))
        for guard, identity in [
            (assert_assessment_baseline_mutable, "BL-A01"),
            (assert_baseline_members_mutable, "BL-A01"),
            (assert_overlay_revision_mutable, "OV-A01"),
            (assert_overlay_memberships_mutable, "OV-A01"),
            (assert_overlay_local_objects_mutable, "OV-A01"),
        ]:
            with pytest.raises(ImmutableRecordError):
                guard(session, identity)


@pytest.mark.parametrize(
    "statement",
    [
        "UPDATE assessment_baselines SET created_at = created_at "
        "WHERE assessment_baseline_id = 'BL-A01'",
        "DELETE FROM assessment_baselines WHERE assessment_baseline_id = 'BL-A01'",
        "INSERT INTO baseline_members (baseline_member_id, "
        "assessment_baseline_id, object_type, object_id, "
        "object_revision_or_state_token, source_identifier, snapshot_payload) "
        "VALUES ('BM-LOCK', 'BL-A01', 'Product Version', 'PV-003', "
        "'A.1', 'lock', '{}')",
        "UPDATE baseline_members SET source_identifier = source_identifier "
        "WHERE assessment_baseline_id = 'BL-A01'",
        "DELETE FROM baseline_members WHERE assessment_baseline_id = 'BL-A01'",
        "UPDATE overlay_revisions SET created_at = created_at WHERE overlay_revision_id = 'OV-A01'",
        "DELETE FROM overlay_revisions WHERE overlay_revision_id = 'OV-A01'",
        "INSERT INTO overlay_change_item_memberships (overlay_revision_id, "
        "change_item_id, change_item_revision) "
        "VALUES ('OV-A01', 'CI-A01', 'r1')",
        "UPDATE overlay_change_item_memberships "
        "SET change_item_revision = change_item_revision "
        "WHERE overlay_revision_id = 'OV-A01'",
        "DELETE FROM overlay_change_item_memberships WHERE overlay_revision_id = 'OV-A01'",
        "INSERT INTO overlay_local_objects (overlay_revision_id, "
        "overlay_local_object_id, object_type, source_change_item_id, "
        "source_change_item_revision, state_payload) "
        "VALUES ('OV-A01', 'OVOBJ-LOCK', 'Product Version', "
        "'CI-A01', 'r1', '{}')",
        "UPDATE overlay_local_objects SET state_payload = state_payload "
        "WHERE overlay_revision_id = 'OV-A01'",
        "DELETE FROM overlay_local_objects WHERE overlay_revision_id = 'OV-A01'",
    ],
)
def test_first_execution_use_is_guarded_by_sqlite_triggers(
    engine, statement: str
) -> None:
    with Session(engine) as session, session.begin():
        _prepare_initial_scenario(session, "A")
        _execute_frozen(session, _execution("A"))

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(text(statement))

    with Session(engine) as session:
        assert session.get(ImpactExecution, "IAX-A01") is not None
        assert session.scalar(
            select(ImpactCandidate).where(
                ImpactCandidate.impact_execution_id == "IAX-A01"
            )
        ) is not None
