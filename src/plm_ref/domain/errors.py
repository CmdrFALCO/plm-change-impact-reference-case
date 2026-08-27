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


class ImpactExecutionLineageError(DomainIntegrityError):
    """Raised before execution when case-local frozen lineage is invalid."""


class ImpactResultValidationError(DomainIntegrityError):
    """Raised when adapter output violates structured impact invariants."""


class RoutingEligibilityError(DomainIntegrityError):
    """Raised when routing cannot start from the execution lifecycle state."""


class RoutingInputError(DomainIntegrityError):
    """Raised when a frozen RRR-v0.1 input cannot be evaluated deterministically."""


class AssessmentCompletionError(DomainIntegrityError):
    """Raised when an Assessment cannot be completed as one frozen semantic unit."""
