"""F4 (1.2.0): DE/EDE mini-tables are independent of group order.

Prior code credited only the first-iterated side of each pair, so the
same logical tournament produced different DE tiers depending on
input order. Pair iteration credits each side's own games to itself.
Covers individual (fide-2024 + fide-2026, Swiss + RR) and team EDE,
plus deterministic fallback under colliding caller keys.
"""
import itertools

from tiebreak_core import fide2024 as f24
from tiebreak_core import fide2026 as f26
from tiebreak_core.models import GameRecord, PlayerTiebreakData
from tiebreak_core.team import (
    TeamFormat,
    TeamMatch,
    TeamRecord,
    rank_team_standings,
)

FMT = TeamFormat(mp_win=2.0, mp_draw=1.0)


def mk(pid, pts, games):
    return PlayerTiebreakData(
        pid, 1500, pts,
        [GameRecord(o, 1500, s, "white", n, kind=k)
         for (o, s, n, k) in games])


def test_win_counts_whichever_side_iterates_first():
    players = {
        1: mk(1, 1.0, [(2, 1.0, 1, "played")]),
        2: mk(2, 0.0, [(1, 0.0, 1, "played")]),
    }
    assert dict(f24._mini_table([1, 2], players)[0]) == {1: 1, 2: 0}
    assert dict(f24._mini_table([2, 1], players)[0]) == {1: 1, 2: 0}
    assert dict(f26._mini_table([1, 2], players, "swiss")[0]) == {1: 1, 2: 0}
    assert dict(f26._mini_table([2, 1], players, "swiss")[0]) == {1: 1, 2: 0}


def test_draw_counts_both_sides():
    players = {
        1: mk(1, 0.5, [(2, 0.5, 1, "played")]),
        2: mk(2, 0.5, [(1, 0.5, 1, "played")]),
    }
    assert dict(f24._mini_table([1, 2], players)[0]) == {1: 0.5, 2: 0.5}
    assert dict(f24._mini_table([2, 1], players)[0]) == {1: 0.5, 2: 0.5}


def test_repeated_meetings_average_per_side():
    players = {
        1: mk(1, 1.0, [(2, 1.0, 1, "played"), (2, 0.0, 2, "played")]),
        2: mk(2, 1.0, [(1, 0.0, 1, "played"), (1, 1.0, 2, "played")]),
    }
    assert dict(f24._mini_table([1, 2], players)[0]) == {1: 0.5, 2: 0.5}
    assert dict(f24._mini_table([2, 1], players)[0]) == {1: 0.5, 2: 0.5}


def _cycle():
    # Rock-paper-scissors results: 1 beats 2, 2 beats 3, 3 beats 1.
    return {
        1: mk(1, 1.0, [(2, 1.0, 1, "played"), (3, 0.0, 2, "played")]),
        2: mk(2, 1.0, [(1, 0.0, 1, "played"), (3, 1.0, 2, "played")]),
        3: mk(3, 1.0, [(1, 1.0, 1, "played"), (2, 0.0, 2, "played")]),
    }


def _tier_sets(tiers):
    return sorted(sorted(tier) for tier in tiers)


def test_tier_permutation_invariance_fide2024():
    # Unresolved tiers preserve input order by design (the ranking
    # layer pre-sorts by deterministic keys); the SETS must agree.
    players = _cycle()
    reference = _tier_sets(f24._de_tiers([1, 2, 3], players))
    for perm in itertools.permutations([1, 2, 3]):
        assert _tier_sets(f24._de_tiers(list(perm), players)) == reference


def test_tier_permutation_invariance_fide2026_modes():
    players = _cycle()
    for mode in ("swiss", "round_robin"):
        reference = _tier_sets(f26._de_tiers([1, 2, 3], players, mode))
        for perm in itertools.permutations([1, 2, 3]):
            assert _tier_sets(
                f26._de_tiers(list(perm), players, mode)) == reference


def test_decisive_tier_exact_order_invariance():
    # A decisive mini-table (1 beats 2 beats 3) resolves identically
    # in every input order, including within-tier order.
    players = {
        1: mk(1, 2.0, [(2, 1.0, 1, "played"), (3, 1.0, 2, "played")]),
        2: mk(2, 1.0, [(1, 0.0, 1, "played"), (3, 1.0, 2, "played")]),
        3: mk(3, 0.0, [(1, 0.0, 1, "played"), (2, 0.0, 2, "played")]),
    }
    for perm in itertools.permutations([1, 2, 3]):
        assert f24._de_tiers(list(perm), players) == [[1], [2], [3]]


def test_ranking_independent_of_input_order():
    players = _cycle()
    first = f24.rank_standings(players, ["direct_encounter"], 2)
    reordered = {pid: players[pid] for pid in (3, 2, 1)}
    second = f24.rank_standings(reordered, ["direct_encounter"], 2)
    assert [p.player_id for p in first.players] == [
        p.player_id for p in second.players]


def test_colliding_keys_fall_back_to_id():
    players = _cycle()
    ranked = f26.rank_standings(players, ["direct_encounter"], 2,
                                deterministic_keys={1: 0, 2: 0, 3: 0})
    # The cycle mini-table ties all three; equal keys -> id order.
    assert [p.player_id for p in ranked.players] == [1, 2, 3]


def test_team_ede_order_invariance():
    teams = {
        1: TeamRecord(1, 3.0, 4.0, [TeamMatch(2, 1, 2, 3.0),
                                    TeamMatch(3, 2, 0, 1.0)]),
        2: TeamRecord(2, 3.0, 4.0, [TeamMatch(1, 1, 0, 1.0),
                                    TeamMatch(3, 2, 2, 3.0)]),
        3: TeamRecord(3, 3.0, 4.0, [TeamMatch(1, 1, 2, 3.0),
                                    TeamMatch(2, 2, 0, 1.0)]),
    }
    first = rank_team_standings(teams, ["EDE"], 2, FMT)
    reordered = {tid: teams[tid] for tid in (3, 2, 1)}
    second = rank_team_standings(reordered, ["EDE"], 2, FMT)
    assert [t.team_id for t in first.teams] == [1, 2, 3]
    assert [t.team_id for t in second.teams] == [1, 2, 3]


def test_team_win_counts_either_order():
    from tiebreak_core.team import _mini_scores
    teams = {
        1: TeamRecord(1, 2.0, 3.0, [TeamMatch(2, 1, 2, 3.0)]),
        2: TeamRecord(2, 0.0, 1.0, [TeamMatch(1, 1, 0, 1.0)]),
    }
    assert dict(_mini_scores([1, 2], teams, "MP")[0]) == {1: 2, 2: 0}
    assert dict(_mini_scores([2, 1], teams, "MP")[0]) == {1: 2, 2: 0}
