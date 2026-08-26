from __future__ import annotations


class DomainIntegrityError(RuntimeError):
    """Base error for deterministic application-level integrity guards."""


class ImmutableRecordError(DomainIntegrityError):
    """Raised when an application command attempts to mutate frozen state."""
