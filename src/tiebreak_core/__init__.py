"""
tiebreak-core — standalone chess tie-break calculation library.

Extracted behavior-preserving from chess-manager ``domain/tiebreak/``.
No Flask, no SQLAlchemy, no persistence, no network.

Calculation (``calculate``/``calculate_all``) and ordering
(``ranking.rank_standings``/``order_ids``) are independent. Tournament
seeding stays outside the core (see ``ranking`` docstring).

Rules versioning: v0.1.0 calculates ``legacy-0.1.0`` only.
See ``tiebreak_core.rules`` and ``docs/KNOWN_LIMITATIONS.md``.
"""

from tiebreak_core.models import (
    GameRecord,
    PlayerTiebreakData,
    TiebreakResult,
    PlayerResult,
    StandingsResult,
)
from tiebreak_core.calculators import (
    buchholz,
    buchholz_cut1,
    buchholz_cut2,
    median_buchholz,
    sonneborn_berger,
    progressive,
    wins_count,
    wins_with_black,
    games_with_black,
    average_rating_opponents,
    koya,
    direct_encounter,
    buchholz_sum,
    arpo,
    calculate,
    calculate_all,
    TIEBREAK_REGISTRY,
)
from tiebreak_core.registry import TIEBREAK_IDS, TIEBREAK_FIDE_REF, DEFAULT_CRITERIA
from tiebreak_core.ranking import rank_standings, order_ids, sort_key
from tiebreak_core.rules import (
    CALCULATION_RULES_VERSION,
    FIDE_REFERENCE,
    SUPPORTED_RULESETS,
    is_supported,
)

__version__ = "0.1.0"
__fide_reference__ = FIDE_REFERENCE
__rules_version__ = CALCULATION_RULES_VERSION

__all__ = [
    "GameRecord",
    "PlayerTiebreakData",
    "TiebreakResult",
    "PlayerResult",
    "StandingsResult",
    "buchholz",
    "buchholz_cut1",
    "buchholz_cut2",
    "median_buchholz",
    "sonneborn_berger",
    "progressive",
    "wins_count",
    "wins_with_black",
    "games_with_black",
    "average_rating_opponents",
    "koya",
    "direct_encounter",
    "buchholz_sum",
    "arpo",
    "calculate",
    "calculate_all",
    "TIEBREAK_REGISTRY",
    "TIEBREAK_IDS",
    "TIEBREAK_FIDE_REF",
    "DEFAULT_CRITERIA",
    "rank_standings",
    "order_ids",
    "sort_key",
    "CALCULATION_RULES_VERSION",
    "FIDE_REFERENCE",
    "SUPPORTED_RULESETS",
    "is_supported",
    "__version__",
    "__fide_reference__",
    "__rules_version__",
]
