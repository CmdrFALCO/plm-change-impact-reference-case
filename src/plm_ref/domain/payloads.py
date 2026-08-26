from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class BaselineProductVersionSnapshot(_StrictPayload):
    product_version_id: str
    product_element_id: str
    revision: str
    iteration: str
    lifecycle_state: str
    material_characteristic: str | None = None
    validated_configuration_scope: str | None = None

    @model_validator(mode="after")
    def technical_state_fields_are_paired(self):
        if (self.material_characteristic is None) != (
            self.validated_configuration_scope is None
        ):
            raise ValueError(
                "material characteristic and validated configuration scope must appear together"
            )
        return self


class BaselineOccurrenceSnapshot(_StrictPayload):
    occurrence_id: str
    parent_product_version_id: str
    child_product_version_id: str
    position: str
    quantity: int
    unit: str
    applicability_rule: ApplicabilityRulePayload
    effectivity_specification: EffectivityPayload


class BaselineConfigurationContextSnapshot(_StrictPayload):
    configuration_context_id: str
    name: str
    feature_values: ConfigurationContextFeatureValues
    completeness_state: str


class BaselineApplicabilityRuleSnapshot(ApplicabilityRulePayload):
    evaluation_in_cfg_001: Literal["Included"] = Field(alias="evaluation_in_CFG-001")
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class BaselineRequirementSnapshot(_StrictPayload):
    requirement_id: str
    requirement_revision: str
    text: str
    allocated_product_element_id: str
    source_class: str
    source_identifier: str
    extraction_timestamp: datetime
