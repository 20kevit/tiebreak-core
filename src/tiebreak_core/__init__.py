"""
tiebreak-core — standalone chess tie-break calculation library.

Extracted behavior-preserving from chess-manager ``domain/tiebreak/``.
No Flask, no SQLAlchemy, no persistence, no network.

Calculation (``calculate``/``calculate_all``) and ordering
(``ranking.rank_standings``/``order_ids``) are independent. Tournament
seeding stays outside the core (see ``ranking`` docstring).

Rules versioning: calculations select an explicit ruleset
(``legacy-0.1.0`` frozen, ``fide-2024`` frozen, ``fide-2026``
implemented). See ``tiebreak_core.rules`` and
``docs/KNOWN_LIMITATIONS.md``.
"""

from tiebreak_core.models import (
    GameRecord,
    PlayerTiebreakData,
    TiebreakResult,
    PlayerResult,
    StandingsResult,
    GAME_KINDS,
    VIRTUAL_KINDS,
    PLAYED,
    PAIRING_BYE,
    FORFEIT_WIN,
    FORFEIT_LOSS,
    REQUESTED_BYE,
    UNPLAYED,
    ABSENT,
    normalize_kind,
)
from tiebreak_core.calculators import (
    buchholz,
    buchholz_cut1,
    buchholz_cut2,
    median_buchholz,
    median_buchholz_2,
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
from tiebreak_core.registry import (
    TIEBREAK_IDS,
    TIEBREAK_FIDE_REF,
    DEFAULT_CRITERIA,
    frozen_registry,
    is_known,
    register_criterion,
    unregister_criterion,
)
from tiebreak_core.errors import (
    TiebreakError,
    UnknownCriterionError,
    UnsupportedRulesetError,
    UnsupportedCriterionError,
    InvalidGameRecordError,
    InvalidPlayerDataError,
    DuplicatePlayerIdError,
    RegistryError,
)
from tiebreak_core.strict import (
    calculate_strict,
    calculate_all_strict,
    rank_standings_strict,
    order_ids_strict,
    validate_game,
    validate_player,
    validate_players,
    require_criteria,
    require_ruleset,
)
from tiebreak_core.ranking import rank_standings, order_ids, sort_key
from tiebreak_core.rules import (
    CALCULATION_RULES_VERSION,
    FIDE_REFERENCE,
    SUPPORTED_RULESETS,
    RulesetInfo,
    available_rulesets,
    describe_ruleset,
    is_supported,
)

__version__ = "0.8.0"
__fide_reference__ = FIDE_REFERENCE
__rules_version__ = CALCULATION_RULES_VERSION

__all__ = [
    "GameRecord",
    "PlayerTiebreakData",
    "TiebreakResult",
    "PlayerResult",
    "StandingsResult",
    "GAME_KINDS",
    "VIRTUAL_KINDS",
    "PLAYED",
    "PAIRING_BYE",
    "FORFEIT_WIN",
    "FORFEIT_LOSS",
    "REQUESTED_BYE",
    "UNPLAYED",
    "ABSENT",
    "normalize_kind",
    "buchholz",
    "buchholz_cut1",
    "buchholz_cut2",
    "median_buchholz",
    "median_buchholz_2",
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
    "frozen_registry",
    "is_known",
    "register_criterion",
    "unregister_criterion",
    "TiebreakError",
    "UnknownCriterionError",
    "UnsupportedRulesetError",
    "UnsupportedCriterionError",
    "InvalidGameRecordError",
    "InvalidPlayerDataError",
    "DuplicatePlayerIdError",
    "RegistryError",
    "calculate_strict",
    "calculate_all_strict",
    "rank_standings_strict",
    "order_ids_strict",
    "validate_game",
    "validate_player",
    "validate_players",
    "require_criteria",
    "require_ruleset",
    "rank_standings",
    "order_ids",
    "sort_key",
    "CALCULATION_RULES_VERSION",
    "FIDE_REFERENCE",
    "SUPPORTED_RULESETS",
    "RulesetInfo",
    "available_rulesets",
    "describe_ruleset",
    "is_supported",
    "__version__",
    "__fide_reference__",
    "__rules_version__",
]
