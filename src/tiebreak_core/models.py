"""
Data models for tiebreak calculations.
Pure Python. No Flask, no SQLAlchemy, no I/O.

v0.1.0: behavior-preserving extraction from chess-manager
``domain/tiebreak/models.py``. Field names, types and semantics are
unchanged. Player/opponent identifiers remain plain ``int`` (compatible
with chess-manager integer IDs). No generic Hashable machinery in v0.1.0.

``GameRecord`` / ``PlayerTiebreakData`` are INPUTS (mutable dataclasses,
as in the original — callers build them then pass them in).
``PlayerResult`` / ``StandingsResult`` are OUTPUTS (frozen, immutable).
"""
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Tuple


# ------------------------------------------------------------------
# Game-kind vocabulary (Phase 1, additive).
#
# Legacy inputs conflate every unplayed/missing game into a single
# ``opponent_id == -1`` sentinel. The vocabulary below lets new inputs
# say WHAT happened instead; legacy calculators ignore it (frozen
# behavior), future rulesets (fide-2026) will branch on it.
# See ADR-006.
# ------------------------------------------------------------------

#: Ordinary played game (real opponent, board result).
PLAYED = "played"
#: Pairing-allocated bye / full-point bye (FIDE C.07 §16.2.1).
PAIRING_BYE = "pairing_bye"
#: Opponent did not arrive / forfeited; full point awarded (§16.2.2).
FORFEIT_WIN = "forfeit_win"
#: Own forfeit loss (§16.2.4).
FORFEIT_LOSS = "forfeit_loss"
#: Requested half/zero-point bye, including post-withdrawal rounds
# (rounds after withdrawal are zero-point byes per §16.1.1). The awarded
# points travel in ``GameRecord.score``; early-vs-trailing distinction
# (§16.2.3 vs §16.2.5) is positional data, not a kind.
REQUESTED_BYE = "requested_bye"
#: Legacy generic: ``opponent_id == -1`` without an explicit kind.
# Preserves legacy arithmetic exactly; carries no FIDE category claim.
UNPLAYED = "unplayed"
#: No pairing/slot at all (round not scheduled for the player).
ABSENT = "absent"

GAME_KINDS: Tuple[str, ...] = (
    PLAYED,
    PAIRING_BYE,
    FORFEIT_WIN,
    FORFEIT_LOSS,
    REQUESTED_BYE,
    UNPLAYED,
    ABSENT,
)

#: Kinds that require ``opponent_id == -1`` (no scheduled opponent).
VIRTUAL_KINDS: Tuple[str, ...] = (
    PAIRING_BYE,
    REQUESTED_BYE,
    UNPLAYED,
    ABSENT,
)


@dataclass
class GameRecord:
    """Single game result for a player."""
    opponent_id: int
    opponent_rating: int
    score: float           # 1.0, 0.5, 0.0
    color: str             # 'white' or 'black'
    round_number: int
    kind: str = ""         # "" = unspecified; see normalize_kind().
    # Explicit kinds (GAME_KINDS) describe unplayed-game semantics for
    # future rulesets. Legacy calculators ignore this field entirely.


def normalize_kind(game: GameRecord) -> str:
    """Return the effective kind of ``game``.

    An explicitly set kind always wins. Unspecified ("") normalizes to
    ``UNPLAYED`` for the legacy ``-1`` sentinel and ``PLAYED`` for real
    opponents — so old inputs keep their exact legacy meaning without
    relabeling anything as FIDE-categorized.
    """
    if game.kind:
        return game.kind
    if game.opponent_id == -1:
        return UNPLAYED
    return PLAYED


@dataclass
class PlayerTiebreakData:
    """
    All data needed for tiebreak calculation for one player.
    """
    player_id: int
    rating: int
    points: float
    games: List[GameRecord] = field(default_factory=list)

    @property
    def opponent_ids(self) -> List[int]:
        return [g.opponent_id for g in self.games]

    @property
    def wins(self) -> int:
        return sum(1 for g in self.games if g.score == 1.0)

    @property
    def wins_with_black(self) -> int:
        return sum(1 for g in self.games if g.score == 1.0 and g.color == 'black')

    @property
    def games_with_black(self) -> int:
        return sum(1 for g in self.games if g.color == 'black')


@dataclass
class TiebreakResult:
    """Tiebreak values for one player (legacy name, kept for compatibility)."""
    player_id: int
    values: Dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class PlayerResult:
    """Immutable per-player calculation result (v0.1.0 output contract)."""
    player_id: int
    points: float
    values: Mapping[str, float] = field(default_factory=dict)
    rank: int = 0  # 0 = unranked; set by ranking.rank_standings()


@dataclass(frozen=True)
class StandingsResult:
    """Immutable ordered standings (v0.1.0 output contract)."""
    players: Tuple[PlayerResult, ...] = ()
    criteria: Tuple[str, ...] = ()
    rules_version: str = "legacy-0.1.0"
