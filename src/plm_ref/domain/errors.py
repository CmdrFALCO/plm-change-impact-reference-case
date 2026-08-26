from __future__ import annotations


class DomainIntegrityError(RuntimeError):
    """Base error for deterministic application-level integrity guards."""


class ImmutableRecordError(DomainIntegrityError):
    """Raised when an application command attempts to mutate frozen state."""


class OverlayExecutionEligibilityError(DomainIntegrityError):
    """Raised when a candidate overlay fails baseline-relative eligibility."""

    def __init__(self, reasons: tuple[str, ...]):
        self.reasons = reasons
        super().__init__("Overlay Execution Eligibility failed: " + "; ".join(reasons))
