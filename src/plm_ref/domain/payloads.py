from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ConfigurationContextFeatureValues(BaseModel):
    """Bounded feature/value shape used by the frozen source fixture."""

    model_config = ConfigDict(extra="forbid")

    PackFamily: str
    CoolingType: str


class ApplicabilityRulePayload(BaseModel):
    """Bounded applicability value object embedded in a source occurrence."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str
    expression: str
    rule_version: str


class EffectivityPayload(BaseModel):
    """Only executable effectivity form in the frozen baseline."""

    model_config = ConfigDict(extra="forbid")

    effectivity_type: Literal["Planned Engineering Effective Date"]
    planned_effective_date: date
