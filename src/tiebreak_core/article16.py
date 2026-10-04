"""
Article 16 policy abstraction (C.07 §§16.1–16.6).

Scattered booleans (``mode``, ``forfeits_as_played``) currently select
unplayed-round behavior at each call site. This module names the
underlying policy so tournament regulations can explicitly override
the FIDE-default behavior where FIDE permits it (§16.6: *"Unless the
rules of a competition specify otherwise, ..."*).

An :class:`Article16Policy` is a value object describing HOW unplayed
rounds are managed; the engines document which policy their defaults
reproduce. New code paths (modifiers, team fore-variants) resolve
their behavior through :func:`resolve_policy`. Existing engine
defaults are unchanged — :func:`default_policy` is pinned by
conformance tests to reproduce ``fide-2024`` / ``fide-2026`` outputs
exactly.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from tiebreak_core.errors import InvalidPlayerDataError

DummyCapMode = Literal["uncapped", "capped"]
ForfeitScope = Literal["swiss", "round_robin", "as_played"]


@dataclass(frozen=True)
class Article16Policy:
    """Named unplayed-round management policy.

    Attributes:
        dummy_cap: ``"uncapped"`` (§16.4 2024: dummy = own score) or
            ``"capped"`` (§16.4.1–16.4.2 2026: forfeit dummies capped
            by the scheduled opponent's adjusted score, other
            unplayed dummies capped by draw-points × rounds).
        late_bye_value: adjusted-score value (§16.3) of a 16.2.5
            trailing requested bye for opponents' use (FIDE: 0.5).
        vur_cut_preference: whether cuts prefer VUR contributions
            (§16.5.1; FIDE: True).
        reapply_cuts: whether the cut exception reapplies per cut
            (§16.5.2; FIDE: True).
        forfeit_scope: ``"swiss"`` (Article 16: forfeits are unplayed
            rounds), ``"round_robin"`` (§15.2 carve-out), or
            ``"as_played"`` (MTB26 ``/P`` regulations opt-in).
        keep_last_element: never cut the final remaining element
            (documented edge guard, not a FIDE rule).
    """

    dummy_cap: DummyCapMode = "capped"
    late_bye_value: float = 0.5
    vur_cut_preference: bool = True
    reapply_cuts: bool = True
    forfeit_scope: ForfeitScope = "swiss"
    keep_last_element: bool = True


FIDE_2024_POLICY = Article16Policy(
    dummy_cap="uncapped",
    late_bye_value=0.5,
    vur_cut_preference=True,
    reapply_cuts=True,
    forfeit_scope="swiss",
    keep_last_element=True,
)

FIDE_2026_SWISS_POLICY = Article16Policy(
    dummy_cap="capped",
    late_bye_value=0.5,
    vur_cut_preference=True,
    reapply_cuts=True,
    forfeit_scope="swiss",
    keep_last_element=True,
)

FIDE_2026_RR_POLICY = Article16Policy(
    dummy_cap="capped",
    late_bye_value=0.5,
    vur_cut_preference=True,
    reapply_cuts=True,
    forfeit_scope="round_robin",
    keep_last_element=True,
)


def resolve_policy(ruleset: str, mode: str = "swiss",
                   forfeits_as_played: bool = False,
                   **overrides) -> Article16Policy:
    """Resolve engine flags to the policy they implement.

    ``§16.6`` overrides pass as keyword overrides (e.g.
    ``late_bye_value=0.0``); unknown override names raise
    :class:`InvalidPlayerDataError` (no silent misconfiguration).
    """
    if ruleset == "fide-2024":
        base = FIDE_2024_POLICY
    elif ruleset == "fide-2026":
        if forfeits_as_played:
            base = Article16Policy(
                dummy_cap="capped", late_bye_value=0.5,
                vur_cut_preference=True, reapply_cuts=True,
                forfeit_scope="as_played", keep_last_element=True)
        elif mode == "round_robin":
            base = FIDE_2026_RR_POLICY
        elif mode == "swiss":
            base = FIDE_2026_SWISS_POLICY
        else:
            raise InvalidPlayerDataError(
                f"mode must be 'swiss' or 'round_robin', got {mode!r}")
    else:
        raise InvalidPlayerDataError(
            f"Article16Policy covers fide-2024/fide-2026, "
            f"got ruleset {ruleset!r}")
    if not overrides:
        return base
    fields = set(base.__dataclass_fields__)
    unknown = [k for k in overrides if k not in fields]
    if unknown:
        raise InvalidPlayerDataError(
            f"unknown Article-16 override(s): {unknown} "
            f"(allowed: {sorted(fields)})")
    if ("late_bye_value" in overrides
            and overrides["late_bye_value"] not in (0.0, 0.5)):
        raise InvalidPlayerDataError(
            "late_bye_value override must be 0.0 or 0.5 "
            f"(§16.3 draw semantics), got "
            f"{overrides['late_bye_value']!r}")
    values = {f: getattr(base, f) for f in fields}
    values.update(overrides)
    return Article16Policy(**values)


__all__ = [
    "Article16Policy",
    "FIDE_2024_POLICY",
    "FIDE_2026_SWISS_POLICY",
    "FIDE_2026_RR_POLICY",
    "resolve_policy",
]
