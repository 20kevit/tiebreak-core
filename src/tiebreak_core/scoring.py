"""
Scoring-scheme model (C.07 Standard Points §7.7 context).

FIDE events may use non-standard point tables (e.g. 3 points for a
win). Most tie-break arithmetic consumes *recorded round scores* and
is agnostic to the table that produced them; two places genuinely
depend on the scheme:

- STD (§7.7): played rounds compare the own score against the
  scheduled opponent's round score (explicit
  ``GameRecord.opponent_score``, else the standard 1–½–0 complement
  when ``draw_points == 0.5``); unplayed rounds compare against the
  event's draw value. Exotic tables without explicit per-round
  opponent scores raise instead of guessing (fide-2026 ``std``).
- Team MP scales (:class:`TeamFormat` carries ``mp_win``/``mp_draw``).

A :class:`ScoringScheme` names the table so consumers pass it
explicitly instead of scattering magic numbers. The standard scheme
is the default everywhere; exotic schemes are representable as data
but only honored where the engines accept explicit inputs — anything
else fails loudly (see :func:`require_standard_or_explicit`).
"""
from __future__ import annotations

from dataclasses import dataclass

from tiebreak_core.errors import InvalidPlayerDataError


@dataclass(frozen=True)
class ScoringScheme:
    """Point table for one event (or one rating/point system leg)."""

    name: str = "standard"
    win: float = 1.0
    draw: float = 0.5
    loss: float = 0.0

    def __post_init__(self) -> None:
        for attr in ("win", "draw", "loss"):
            value = getattr(self, attr)
            if (isinstance(value, bool)
                    or not isinstance(value, (int, float))):
                raise InvalidPlayerDataError(
                    f"ScoringScheme.{attr} must be a number, "
                    f"got {value!r}")
        if not (self.win > self.draw >= self.loss):
            raise InvalidPlayerDataError(
                f"ScoringScheme needs win > draw >= loss, got "
                f"{self!r}")


STANDARD = ScoringScheme(name="standard", win=1.0, draw=0.5, loss=0.0)


def is_standard(scheme: ScoringScheme) -> bool:
    """True iff ``scheme`` is the standard 1–½–0 table."""
    return (scheme.win == 1.0 and scheme.draw == 0.5
            and scheme.loss == 0.0)


def require_standard_or_explicit(scheme: ScoringScheme,
                                opponent_score: float | None,
                                context: str) -> float | None:
    """Resolve the scheduled-opponent round score for STD-like logic.

    Returns the explicit ``opponent_score`` when given; derives the
    standard complement (``win - own``) for standard schemes;
    raises :class:`InvalidPlayerDataError` for exotic schemes without
    explicit scores (the core must not invent the table's complement).
    """
    if opponent_score is not None:
        return opponent_score
    if is_standard(scheme):
        return None  # caller derives the 1-½-0 complement
    raise InvalidPlayerDataError(
        f"{context}: non-standard scoring scheme {scheme.name!r} "
        f"requires explicit per-round opponent scores "
        f"(GameRecord.opponent_score); refusing to guess the table")


__all__ = [
    "ScoringScheme",
    "STANDARD",
    "is_standard",
    "require_standard_or_explicit",
]
