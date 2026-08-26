from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict

from plm_ref.infrastructure.impact.port import (
    ImpactCandidateSpec,
    ImpactExecutionContext,
)


DEFAULT_IMPACT_FIXTURE_DIRECTORY = (
    Path(__file__).resolve().parents[4] / "data" / "impact-fixtures"
)


class _ImpactFixture(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidates: tuple[ImpactCandidateSpec, ...]


EXPECTED_CONTEXTS = {
    "IAX-A01": {
        "change_case_id": "CHG-A01",
        "assessment_baseline_id": "BL-A01",
        "overlay_revision_id": "OV-A01",
        "overlay_membership": (("CI-A01", "r1"),),
        "overlay_local_object_ids": ("OVOBJ-A01-PV",),
    },
    "IAX-B01": {
        "change_case_id": "CHG-B01",
        "assessment_baseline_id": "BL-B01",
        "overlay_revision_id": "OV-B01",
        "overlay_membership": (("CI-B01", "r1"),),
        "overlay_local_object_ids": ("OVOBJ-B01-PV",),
    },
    "IAX-B02": {
        "change_case_id": "CHG-B01",
        "assessment_baseline_id": "BL-B01",
        "overlay_revision_id": "OV-B02",
        "overlay_membership": (("CI-B01", "r1"), ("CI-B02", "r1")),
        "overlay_local_object_ids": ("OVOBJ-B02-PSO", "OVOBJ-B02-PV"),
    },
    "IAX-C01": {
        "change_case_id": "CHG-C01",
        "assessment_baseline_id": "BL-C01",
        "overlay_revision_id": "OV-C01",
        "overlay_membership": (("CI-C01", "r1"),),
        "overlay_local_object_ids": ("OVOBJ-C01-PV",),
    },
}


class FrozenFixtureImpactAdapter:
    """Deterministic INC-05 adapter for the four frozen executions only."""

    def __init__(self, fixture_directory: str | Path | None = None) -> None:
        self.fixture_directory = (
            Path(fixture_directory)
            if fixture_directory is not None
            else DEFAULT_IMPACT_FIXTURE_DIRECTORY
        )

    def run(
        self, context: ImpactExecutionContext
    ) -> tuple[ImpactCandidateSpec, ...]:
        expected = EXPECTED_CONTEXTS.get(context.impact_execution_id)
        if expected is None:
            raise ValueError(
                f"unsupported frozen Impact-analysis Execution "
                f"{context.impact_execution_id}"
            )

        actual_membership = tuple(
            sorted(
                (item.change_item_id, item.change_item_revision)
                for item in context.overlay_membership
            )
        )
        actual = {
            "change_case_id": context.change_case_id,
            "assessment_baseline_id": context.assessment_baseline_id,
            "overlay_revision_id": context.overlay_revision_id,
            "overlay_membership": actual_membership,
            "overlay_local_object_ids": tuple(
                sorted(context.overlay_local_object_ids)
            ),
        }
        if context.rule_set_version != "RRR-v0.1" or actual != expected:
            raise ValueError(
                f"frozen lineage mismatch for {context.impact_execution_id}"
            )

        fixture_path = self.fixture_directory / f"{context.impact_execution_id}.yaml"
        with fixture_path.open("r", encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)
        fixture = _ImpactFixture.model_validate(raw)
        return fixture.candidates
