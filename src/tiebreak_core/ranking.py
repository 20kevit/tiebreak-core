"""
Ranking comparator (ordering only — no calculation, no seeding).

Scope decision (v0.1.0, per architectural correction):
  - tiebreak-core OWNS: ``rank_standings()`` — a reusable, pure ordering
    over explicitly supplied ``(points, tiebreak values, deterministic key)``.
  - chess-manager OWNS (outside the core): initial seeding
    (``current_round == 0`` → rating_snapshot DESC, start_number ASC),
    pairing_no/start_number assignment, tournament lifecycle
    (setup/ongoing/finished), registration/withdrawal filtering.

``rank_standings`` therefore takes pre-calculated values + an explicit
``tiebreak order`` + an explicit deterministic fallback key per player.
It never reads ``current_round``, ``status`` or ``rating_snapshot`` and
never performs seeding. Seeding helpers are intentionally absent.
"""
from typing import Dict, List, Mapping, Sequence, Tuple

from tiebreak_core.models import PlayerResult, PlayerTiebreakData, StandingsResult
from tiebreak_core.calculators import calculate_all
from tiebreak_core.rules import CALCULATION_RULES_VERSION


def sort_key(
    points: float,
    values: Mapping[str, float],
    criteria: Sequence[str],
    deterministic_key: int = 0,
) -> Tuple:
    """Pure ranking key: (-points, -criterion..., deterministic_key).

    ``deterministic_key`` is the caller's stable fallback
    (chess-manager passes ``pairing_no or start_number or 999``).
    """
    return tuple([-points] + [-values.get(c, 0) for c in criteria] + [deterministic_key])


def rank_standings(
    players: Mapping[int, PlayerTiebreakData],
    criteria: Sequence[str],
    total_rounds: int = 0,
    deterministic_keys: Mapping[int, int] | None = None,
) -> StandingsResult:
    """Calculate values for every player and return them in rank order.

    Composable: callers that only need values should use
    ``calculate``/``calculate_all`` directly and skip this function.
    """
    keys = deterministic_keys or {}
    scored: List[PlayerResult] = []
    for pid, pdata in players.items():
        values = calculate_all(pdata, dict(players), list(criteria), total_rounds)
        scored.append(PlayerResult(
            player_id=pid,
            points=pdata.points or 0.0,
            values=dict(values),
            rank=0,
        ))

    def _key(pr: PlayerResult) -> Tuple:
        return sort_key(pr.points, pr.values, criteria, keys.get(pr.player_id, pr.player_id))

    ordered = sorted(scored, key=_key)
    ranked = tuple(
        PlayerResult(player_id=pr.player_id, points=pr.points,
                     values=pr.values, rank=i + 1)
        for i, pr in enumerate(ordered)
    )
    return StandingsResult(
        players=ranked,
        criteria=tuple(criteria),
        rules_version=CALCULATION_RULES_VERSION,
    )


def order_ids(
    points: Mapping[int, float],
    values: Mapping[int, Mapping[str, float]],
    criteria: Sequence[str],
    deterministic_keys: Mapping[int, int] | None = None,
) -> List[int]:
    """Order player ids without recalculating (pure comparator)."""
    keys = deterministic_keys or {}

    def _key(pid: int) -> Tuple:
        return sort_key(points.get(pid, 0.0), values.get(pid, {}),
                        criteria, keys.get(pid, pid))

    return sorted(points.keys(), key=_key)
