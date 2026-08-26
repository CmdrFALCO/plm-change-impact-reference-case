from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict


class _StrictPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ConfigurationContextFeatureValues(_StrictPayload):
    """Bounded feature/value shape used by the frozen source fixture."""

    PackFamily: str
    CoolingType: str


class ApplicabilityRulePayload(_StrictPayload):
    """Bounded applicability value object embedded in source/overlay state."""

    rule_id: str
    expression: str
    rule_version: str


class EffectivityPayload(_StrictPayload):
    """Only executable effectivity form in the frozen baseline."""

    effectivity_type: Literal["Planned Engineering Effective Date"]
    planned_effective_date: date


class ReviseProductStateCurrentReference(_StrictPayload):
    product_version_id: str
    revision: str
    iteration: str


class ReviseProductStateProposalPayload(_StrictPayload):
    product_element_id: str
    proposed_revision: str
    proposed_iteration: str
    supersedes_product_version_id: str
    material_characteristic: str
    validated_configuration_scope: str
    intended_function_change: bool


class ChangeApplicabilityCurrentReference(_StrictPayload):
    occurrence_id: str
    applicability_rule_id: str
    applicability_rule_version: str


class ChangeApplicabilityProposalPayload(_StrictPayload):
    applicability_rule: ApplicabilityRulePayload
