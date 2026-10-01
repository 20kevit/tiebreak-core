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


@dataclass
class GameRecord:
    """Single game result for a player."""
    opponent_id: int
    opponent_rating: int
    score: float           # 1.0, 0.5, 0.0
    color: str             # 'white' or 'black'
    round_number: int


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
