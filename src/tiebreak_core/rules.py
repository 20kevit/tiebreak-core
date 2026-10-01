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
"""
from typing import Tuple

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
