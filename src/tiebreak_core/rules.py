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

SUPPORTED_RULESETS: Tuple[str, ...] = ("legacy-0.1.0", "fide-2024", "fide-2026")

ROADMAP_RULESETS: Tuple[str, ...] = ("FIDE_2024", "FIDE_2026")


def is_supported(rules_version: str) -> bool:
    """Return True iff this library version can calculate rules_version."""
    return rules_version in SUPPORTED_RULESETS


@dataclass(frozen=True)
class RulesetInfo:
    """Inspectable metadata for one ruleset (implemented or specified).

    Attributes:
        id: ruleset identifier used in ``ruleset=`` selection and
            ``StandingsResult.rules_version``.
        status: "implemented" (calculations available) or "specified"
            (researched and specified, implementation pending;
            requesting calculation raises ``UnsupportedRulesetError``).
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
            "median_buchholz", "median_buchholz_2", "sonneborn_berger", "progressive",
            "wins", "wins_black", "games_black", "aro", "koya",
            "buchholz_sum", "arpo", "direct_encounter",
        ),
    ),
    "fide-2026": RulesetInfo(
        id="fide-2026",
        status="implemented",
        description=(
            "FIDE C.07 edition effective 1 Mar 2026 for individual "
            "tournaments: the full fide-2024 Swiss engine plus the "
            "§16.4 dummy caps (16.4.1 scheduled-opponent cap for "
            "forfeits; 16.4.2 draw-points x rounds cap otherwise), an "
            "explicit swiss/round_robin mode flag (round_robin "
            "implements the §15.2 forfeit carve-out), and terminal "
            "ranking stages tpn (§7.8) / rtng (§10.6). "
            "Out of scope: Standard Points §7.7 (needs "
            "scheduled-opponent round scores, Phase F26-2), team "
            "systems §§11–13, Art.16.6 overrides, Koya-limit §14.5. "
            "Buchholz-family use in round-robins is documented, not "
            "enforced (Art. 8 note)."
        ),
        fide_reference=(
            "FIDE Handbook C.07 Play-Off and Tie-Break Regulations "
            "(effective from 1 Mar 2026; approved by FIDE Council "
            "02/02/2026)."
        ),
        criteria=(
            "buchholz", "buchholz_cut1", "buchholz_cut2",
            "median_buchholz", "median_buchholz_2", "sonneborn_berger",
            "sonneborn_berger_cut1", "sonneborn_berger_cut2",
            "progressive", "progressive_cut1",
            "wins", "won", "games_black", "wins_black", "rounds_elected",
            "std",             "aro", "aro_cut1", "aro_cut2", "aro_median1", "aro_median2",
            "aob", "aob_fb",
            "fore_buchholz", "fore_buchholz_cut1", "fore_buchholz_cut2",
            "fore_median1", "fore_median2",
            "koya", "tpr", "ptp", "apro", "appo",
        ),
    ),
    "fide-2024": RulesetInfo(
        id="fide-2024",
        status="implemented",
        description=(
            "FIDE-correct calculations for individual Swiss tournaments: "
            "Article 16 unplayed-round management (categories, adjusted "
            "scores, dummy rule, cut exception), Cut/Median modifiers, "
            "SB-C1/PS-C1/ARO-C1, AOB, Fore Buchholz, over-the-board "
            "Type-B semantics, Koya threshold on maximum possible score, "
            "rating family (TPR/PTP/APRO/APPO from the official §8.1a/§8.1b "
            "tables). "
            "Out of scope: team systems, Direct Encounter (Phase 3), "
            "Art.16.6 overrides."
        ),
        fide_reference=(
            "FIDE Council document 2024_FC2_18, PLAY-OFF AND TIE-BREAK "
            "REGULATIONS (approved 29/07/2024, applied 1 Aug 2024)."
        ),
        criteria=(
            "buchholz", "buchholz_cut1", "buchholz_cut2",
            "median_buchholz", "median_buchholz_2", "sonneborn_berger",
            "sonneborn_berger_cut1", "progressive", "progressive_cut1",
            "wins", "won", "games_black", "wins_black", "rounds_elected",
            "aro", "aro_cut1", "aob", "fore_buchholz", "koya",
            "tpr", "ptp", "apro", "appo",
        ),
    ),
}


def available_rulesets() -> Tuple[RulesetInfo, ...]:
    """Return metadata for every known ruleset (implemented + specified)."""
    return tuple(_RULESETS.values())


def describe_ruleset(ruleset: str) -> RulesetInfo:
    """Return metadata for ``ruleset``.

    Raises ``UnsupportedRulesetError`` for ids the library does not know
    at all. Specified (not yet implemented) rulesets return their
    descriptor (with ``status="specified"``); calculation under them is
    still refused by the strict path.
    """
    from tiebreak_core.errors import UnsupportedRulesetError

    try:
        return _RULESETS[ruleset]
    except KeyError:
        raise UnsupportedRulesetError(
            ruleset, tuple(_RULESETS)) from None
