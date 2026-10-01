"""Ranking comparator tests — verifies explicit-policy ordering.

Covers: criteria ordering, deterministic fallback, composability of
calculate_all vs rank_standings, and that seeding is NOT in the core.
"""
from tiebreak_core.models import PlayerTiebreakData, GameRecord
from tiebreak_core.calculators import calculate_all
from tiebreak_core.ranking import rank_standings, order_ids, sort_key


def rec(opp, score, rnd=1, color="white"):
    return GameRecord(opponent_id=opp, opponent_rating=1500,
                      score=score, color=color, round_number=rnd)


def test_sort_key_points_then_tiebreak_then_key():
    # Same points: higher buchholz first.
    k1 = sort_key(2.0, {"buchholz": 5.0}, ["buchholz"], 2)
    k2 = sort_key(2.0, {"buchholz": 3.0}, ["buchholz"], 1)
    assert k1 < k2
    # Higher points always first regardless of tiebreak.
    k3 = sort_key(3.0, {"buchholz": 0.0}, ["buchholz"], 99)
    assert k3 < k1
    # Full tie -> deterministic key decides.
    ka = sort_key(1.0, {"buchholz": 1.0}, ["buchholz"], 1)
    kb = sort_key(1.0, {"buchholz": 1.0}, ["buchholz"], 2)
    assert ka < kb


def test_rank_standings_order_matches_legacy_sort():
    p1 = PlayerTiebreakData(1, 2000, 2.5,
                            [rec(2, 1, 1), rec(3, 0.5, 2), rec(4, 1, 3)])
    p2 = PlayerTiebreakData(2, 1900, 1.0,
                            [rec(1, 0, 1), rec(3, 0.5, 2), rec(4, 0.5, 3)])
    p3 = PlayerTiebreakData(3, 1800, 1.5,
                            [rec(1, 0.5, 1), rec(2, 0.5, 2), rec(4, 0.5, 3)])
    p4 = PlayerTiebreakData(4, 1700, 1.0,
                            [rec(1, 0, 1), rec(2, 0.5, 2), rec(3, 0.5, 3)])
    players = {1: p1, 2: p2, 3: p3, 4: p4}
    criteria = ["buchholz_cut1", "buchholz", "sonneborn_berger", "progressive"]
    res = rank_standings(players, criteria, total_rounds=3,
                         deterministic_keys={1: 1, 2: 2, 3: 3, 4: 4})
    assert res.criteria == tuple(criteria)
    assert res.rules_version == "legacy-0.1.0"
    # Legacy sort: points DESC, then criteria DESC, then rank_no ASC.
    assert res.players[0].player_id == 1
    assert [p.rank for p in res.players] == [1, 2, 3, 4]
    # Values composable: rank_standings values == calculate_all values.
    for pr in res.players:
        assert pr.values == calculate_all(
            players[pr.player_id], players, criteria, 3)


def test_order_ids_pure_comparator():
    points = {1: 2.0, 2: 2.0, 3: 1.0}
    values = {1: {"buchholz": 3.0}, 2: {"buchholz": 5.0}, 3: {"buchholz": 9.0}}
    assert order_ids(points, values, ["buchholz"], {1: 1, 2: 2, 3: 3}) == [2, 1, 3]


def test_no_seeding_in_core():
    # rank_standings has no current_round / rating-seeding branch:
    # two scoreless players order purely by explicit deterministic key.
    p1 = PlayerTiebreakData(1, 2200, 0.0, [])
    p2 = PlayerTiebreakData(2, 1200, 0.0, [])
    res = rank_standings({1: p1, 2: p2}, ["buchholz"],
                         deterministic_keys={1: 2, 2: 1})
    assert [p.player_id for p in res.players] == [2, 1]
