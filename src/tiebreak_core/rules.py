"""
Rule/version model for tiebreak-core.

v0.1.0 implements ONE ruleset only: the behavior-preserving legacy
extraction from chess-manager ("legacy-0.1.0"). No FIDE corrections are
applied. This module exists so future rulesets (e.g. FIDE_2024, FIDE_2026
with Article 16 unplayed-round management) can be added WITHOUT silently
changing historical results.

Contract:
  - Every calculation records which ruleset produced it
    (see StandingsResult.rules_version / CALCULATION_RULES_VERSION).
  - New rulesets MUST be added as new version strings + new code paths,
    never by editing legacy behavior in place.
  - Reproducibility: same inputs + same rules_version => same outputs.
  - Ruleset metadata is inspectable via describe_ruleset() /
    available_rulesets() (see ADR-001). Reserved (not yet implemented)
    rulesets are described but rejected at calculation time.
"""
from dataclasses import dataclass
from typing import Dict, Tuple

CALCULATION_RULES_VERSION = "legacy-0.1.0"

FIDE_REFERENCE = (
    "Behavior-preserving extraction of chess-manager domain/tiebreak "
    "(pre-FIDE-C.07-Article-16-correction). "
    "Reference for future work: FIDE Handbook C.07 Play-Off and Tie-Break "
    "Regulations (effective 1 Aug 2024 till 28 Feb 2026; successor from "
    "1 Mar 2026). See docs/TIEBREAK_RULES.md and docs/KNOWN_LIMITATIONS.md."
)

SUPPORTED_RULESETS: Tuple[str, ...] = ("legacy-0.1.0",)

ROADMAP_RULESETS: Tuple[str, ...] = ("FIDE_2024", "FIDE_2026")


def is_supported(rules_version: str) -> bool:
    """Return True iff this library version can calculate rules_version."""
    return rules_version in SUPPORTED_RULESETS


@dataclass(frozen=True)
class RulesetInfo:
    """Inspectable metadata for one ruleset (implemented or reserved).

    Attributes:
        id: ruleset identifier used in ``ruleset=`` selection and
            ``StandingsResult.rules_version``.
        status: "implemented" (calculations available) or "reserved"
            (name claimed for future work; requesting it raises
            ``UnsupportedRulesetError``).
        description: what behavior this ruleset pins.
        fide_reference: authoritative source the ruleset tracks.
        criteria: criterion ids defined under this ruleset.
    """

    id: str
    status: str
    description: str
    fide_reference: str
    criteria: Tuple[str, ...] = ()


_RULESETS: Dict[str, RulesetInfo] = {
    "legacy-0.1.0": RulesetInfo(
        id="legacy-0.1.0",
        status="implemented",
        description=(
            "Behavior-preserving extraction of chess-manager "
            "domain/tiebreak (pre-FIDE-C.07-Article-16-correction). "
            "Frozen: outputs never change."
        ),
        fide_reference=(
            "FIDE Handbook C.07 Play-Off and Tie-Break Regulations "
            "(effective 1 Aug 2024 till 28 Feb 2026) — used as a "
            "divergence reference only, see docs/KNOWN_LIMITATIONS.md."
        ),
        criteria=(
            "buchholz", "buchholz_cut1", "buchholz_cut2",
            "median_buchholz", "sonneborn_berger", "progressive",
            "wins", "wins_black", "games_black", "aro", "koya",
            "buchholz_sum", "arpo", "direct_encounter",
        ),
    ),
    "fide-2026": RulesetInfo(
        id="fide-2026",
        status="reserved",
        description=(
            "Future FIDE-correct behavior (unplayed-round taxonomy, "
            "Article 16 virtual opponents, full Direct Encounter, "
            "complete rating-based family). Not implemented."
        ),
        fide_reference=(
            "FIDE Handbook C.07 Play-Off and Tie-Break Regulations "
            "(effective from 1 Mar 2026; approved by FIDE Council "
            "02/02/2026)."
        ),
        criteria=(),
    ),
}


def available_rulesets() -> Tuple[RulesetInfo, ...]:
    """Return metadata for every known ruleset (implemented + reserved)."""
    return tuple(_RULESETS.values())


def describe_ruleset(ruleset: str) -> RulesetInfo:
    """Return metadata for ``ruleset``.

    Raises ``UnsupportedRulesetError`` for ids the library does not know
    at all. Reserved rulesets return their descriptor (with
    ``status="reserved"``); calculation under them is still refused by
    the strict path.
    """
    from tiebreak_core.errors import UnsupportedRulesetError

    try:
        return _RULESETS[ruleset]
    except KeyError:
        raise UnsupportedRulesetError(
            ruleset, tuple(_RULESETS)) from None
