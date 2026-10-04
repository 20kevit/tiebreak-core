"""
Typed validation errors for tiebreak-core (Phase 0, additive).

The legacy calculation path (``calculators.calculate`` / ``calculate_all``)
never raises these: unknown criteria silently yield ``0.0`` there, and that
behavior is frozen under ``legacy-0.1.0``. The strict path
(``tiebreak_core.strict``) raises the errors below instead. New code that
wants fail-fast contracts should use the strict path; existing callers are
unaffected.
"""
from __future__ import annotations


class TiebreakError(Exception):
    """Base class for all tiebreak-core errors."""


class UnknownCriterionError(TiebreakError):
    """Raised when a criterion id is not a known built-in (or registered custom)."""

    def __init__(self, criterion: object) -> None:
        self.criterion = criterion
        super().__init__(f"unknown tie-break criterion: {criterion!r}")


class UnsupportedRulesetError(TiebreakError):
    """Raised when a ruleset other than a supported one is requested."""
    def __init__(self, ruleset: object, supported: tuple = ("legacy-0.1.0",)) -> None:
        self.ruleset = ruleset
        self.supported = supported
        super().__init__(
            f"unsupported ruleset: {ruleset!r} "
            f"(supported: {', '.join(supported)})."
        )


class InvalidGameRecordError(TiebreakError):
    """Raised when a GameRecord carries values the calculators cannot interpret."""


class UnsupportedCriterionError(TiebreakError):
    """Raised when a known criterion is not implemented under a ruleset
    (e.g. rating-table systems under fide-2024)."""

    def __init__(self, criterion: object, ruleset: object) -> None:
        self.criterion = criterion
        self.ruleset = ruleset
        super().__init__(
            f"criterion {criterion!r} is not implemented under ruleset "
            f"{ruleset!r}")


class InvalidPlayerDataError(TiebreakError):
    """Raised when a PlayerTiebreakData (or players mapping) is malformed."""


class DuplicatePlayerIdError(InvalidPlayerDataError):
    """Raised when two players share one id where unique ids are required."""


class RegistryError(TiebreakError):
    """Raised on illegal registry operations (e.g. overwriting a built-in)."""


class InvalidDescriptorError(TiebreakError):
    """Raised when an MTB26 rank-order descriptor is malformed or
    combines modifiers FIDE does not define (e.g. ``SB/M1``)."""

    def __init__(self, descriptor: object, reason: str = "") -> None:
        self.descriptor = descriptor
        self.reason = reason
        detail = f": {reason}" if reason else ""
        super().__init__(
            f"invalid MTB26 descriptor {descriptor!r}{detail}")
