from __future__ import annotations

from collections.abc import Sequence
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field


class _FrozenImpactValue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ChangeItemRevisionReference(_FrozenImpactValue):
    change_item_id: str
    change_item_revision: str


class ImpactExecutionContext(_FrozenImpactValue):
    impact_execution_id: str
    change_case_id: str
    assessment_baseline_id: str
    overlay_revision_id: str
    rule_set_version: Literal["RRR-v0.1"]
    overlay_membership: tuple[ChangeItemRevisionReference, ...]
    overlay_local_object_ids: tuple[str, ...]


class DependencyPathStepSpec(_FrozenImpactValue):
    sequence: int = Field(ge=1)
    source_reference: str
    relationship_type: str
    target_reference: str
    state_context: Literal["Current State", "Proposed State"]


class ImpactCandidateProvenanceSpec(_FrozenImpactValue):
    impact_candidate_provenance_id: str
    change_item_id: str
    change_item_revision: str
    dependency_path: tuple[DependencyPathStepSpec, ...] = Field(min_length=1)


class ImpactCandidateSpec(_FrozenImpactValue):
    impact_candidate_id: str
    candidate_type: str
    candidate_reference: str
    affected_domain: str
    provenance: tuple[ImpactCandidateProvenanceSpec, ...] = Field(min_length=1)


class ImpactAnalysisPort(Protocol):
    """Boundary for bounded impact discovery.

    The port returns only candidate and provenance data. Execution state and
    downstream routing/assessment state remain application-owned.
    """

    def run(
        self, context: ImpactExecutionContext
    ) -> Sequence[ImpactCandidateSpec]: ...
