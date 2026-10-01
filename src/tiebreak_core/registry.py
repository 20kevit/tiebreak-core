"""
Tie-break registry metadata (identifiers only).

The calculation path (calculators.py) depends ONLY on the stable string
identifiers below. Human-readable presentation strings live in
``tiebreak_core.display`` and must never affect calculation or ranking.
"""
from typing import Dict, List, Tuple

TIEBREAK_IDS: Tuple[str, ...] = (
    "buchholz",
    "buchholz_cut1",
    "buchholz_cut2",
    "median_buchholz",
    "sonneborn_berger",
    "progressive",
    "wins",
    "wins_black",
    "games_black",
    "aro",
    "koya",
    "buchholz_sum",
    "arpo",
    "direct_encounter",
)

# FIDE C.07 cross-reference for roadmap work (informational only in v0.1.0).
TIEBREAK_FIDE_REF: Dict[str, str] = {
    "buchholz": "C.07 §8.1 BH",
    "buchholz_cut1": "C.07 §14.1a BH-C1",
    "buchholz_cut2": "C.07 §14.2 BH-C2",
    "median_buchholz": "C.07 §14.3 BH-M1",
    "sonneborn_berger": "C.07 §9.1 SB",
    "progressive": "C.07 §7.5 PS",
    "wins": "C.07 §7.1 WIN/WON",
    "wins_black": "C.07 §7.4 BWG",
    "games_black": "C.07 §7.3 BPG",
    "aro": "C.07 §10.1 ARO",
    "koya": "C.07 §9.2 KS (RR-only per FIDE; legacy applies to Swiss)",
    "buchholz_sum": "non-FIDE extension (Buchholz of Buchholz)",
    "arpo": "C.07 §10.4 APRO (legacy uses simplified dp table)",
    "direct_encounter": "C.07 §6 DE (legacy standings-level value is a 0.0 stub)",
}

DEFAULT_CRITERIA: List[str] = [
    "buchholz_cut1",
    "buchholz",
    "sonneborn_berger",
    "progressive",
]
