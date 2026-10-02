"""Frozen legacy contract — pins that MUST hold under ``legacy-0.1.0``.

If any of these fail, the legacy path changed: do NOT "fix" the expected
value — record a finding. Complements the golden fixtures
(``data_goldens.json``) with explicit rounding, unplayed-game,
withdrawal-ownership and ordering pins.
"""
import pytest

from tiebreak_core import calculate, calculate_all, rank_standings
from tiebreak_core.models import PlayerTiebreakData, GameRecord


def rec(opp, score, color="white", rnd=1, opp_rating=1500):
    return GameRecord(opponent_id=opp, opponent_rating=opp_rating,
                      score=score, color=color, round_number=rnd)


class TestRoundingFrozen:
    def test_buchholz_one_decimal(self):
        # 3 opponents: 1.0 + 1.5 + 1.0 -> 3.5 exact; rounding path pinned
        # via a fractional SB below and ARO integer rounding.
        p = PlayerTiebreakData(1, 1500, 2.0,
                               [rec(2, 1, rnd=1), rec(3, 0.5, rnd=2)])
        allp = {1: p, 2: PlayerTiebreakData(2, 1500, 1.0, []),
                3: PlayerTiebreakData(3, 1500, 1.5, [])}
        assert calculate(p, allp, "buchholz") == 2.5
        # SB = 1.0*1.0 + 1.5*0.5 = 1.75, kept at 2 decimals
        assert calculate(p, allp, "sonneborn_berger") == 1.75

    def test_aro_integer_rounding(self):
        p = PlayerTiebreakData(1, 1500, 1.0, [rec(2, 1), rec(3, 0)])
        allp = {1: p, 2: PlayerTiebreakData(2, 1601, 0, []),
                3: PlayerTiebreakData(3, 1600, 0, [])}
        # (1601 + 1600) / 2 = 1600.5 -> round() -> 1600 (banker's)
        assert calculate(p, allp, "aro") == round(1600.5)


class TestVirtualOpponentFrozen:
    def test_bye_counts_self_minus_score(self):
        # points 3.0, bye win (1.0): virtual contribution = 2.0
        p = PlayerTiebreakData(1, 1500, 3.0,
                               [rec(-1, 1.0, rnd=1), rec(2, 1.0, rnd=2)])
        allp = {1: p, 2: PlayerTiebreakData(2, 1500, 1.0, [])}
        assert calculate(p, allp, "buchholz") == 3.0  # 2.0 + 1.0

    def test_half_bye_virtual(self):
        p = PlayerTiebreakData(1, 1500, 1.5, [rec(-1, 0.5, rnd=1)])
        assert calculate(p, {1: p}, "buchholz") == 1.0

    def test_forfeit_win_is_virtual_too(self):
        # Legacy cannot distinguish bye vs forfeit win: same -1 handling.
        p = PlayerTiebreakData(1, 1500, 2.0, [rec(-1, 1.0, rnd=1)])
        assert calculate(p, {1: p}, "buchholz") == 1.0
        assert calculate(p, {1: p}, "sonneborn_berger") == 1.0

    def test_aro_uses_own_rating_for_virtual(self):
        p = PlayerTiebreakData(1, 1800, 1.0, [rec(-1, 1.0)])
        assert calculate(p, {1: p}, "aro") == 1800

    def test_missing_opponent_skipped(self):
        # Opponent id absent from the map: silently skipped (frozen).
        p = PlayerTiebreakData(1, 1500, 1.0, [rec(99, 1.0)])
        assert calculate(p, {1: p}, "buchholz") == 0.0


class TestZeroGameAndWithdrawalOwnership:
    def test_zero_game_player_all_zeros(self):
        p = PlayerTiebreakData(1, 1500, 0.0, [])
        allp = {1: p}
        for crit in ["buchholz", "buchholz_cut1", "buchholz_cut2",
                     "median_buchholz", "sonneborn_berger", "progressive",
                     "aro", "koya", "arpo", "buchholz_sum"]:
            assert calculate(p, allp, crit, total_rounds=4) == 0.0

    def test_withdrawn_like_player_sorts_last(self):
        # The core has NO withdrawal marker: a withdrawn-with-points player
        # is ranked purely on numbers. Filtering is caller-owned (manager).
        active = PlayerTiebreakData(1, 1500, 2.0, [])
        ghost = PlayerTiebreakData(2, 1500, 2.0, [])
        res = rank_standings({1: active, 2: ghost}, ["buchholz"],
                             deterministic_keys={1: 1, 2: 2})
        assert [pr.player_id for pr in res.players] == [1, 2]
        assert res.rules_version == "legacy-0.1.0"


class TestOrderingFrozen:
    def test_points_dominate_tiebreaks(self):
        low = PlayerTiebreakData(1, 1500, 1.0, [rec(2, 0, rnd=1)])
        high = PlayerTiebreakData(2, 1500, 3.0, [rec(1, 1, rnd=1)])
        res = rank_standings({1: low, 2: high}, ["buchholz"],
                             deterministic_keys={1: 1, 2: 2})
        assert [pr.player_id for pr in res.players] == [2, 1]

    def test_full_tie_falls_to_deterministic_key(self):
        a = PlayerTiebreakData(1, 1500, 1.0, [])
        b = PlayerTiebreakData(2, 1500, 1.0, [])
        res = rank_standings({1: a, 2: b}, ["buchholz"],
                             deterministic_keys={1: 5, 2: 3})
        assert [pr.player_id for pr in res.players] == [2, 1]

    def test_ranks_sequential_from_one(self):
        players = {i: PlayerTiebreakData(i, 1500, float(4 - i), [])
                   for i in (1, 2, 3)}
        res = rank_standings(players, ["buchholz"],
                             deterministic_keys={1: 1, 2: 2, 3: 3})
        assert [pr.rank for pr in res.players] == [1, 2, 3]
        assert res.criteria == ("buchholz",)

    def test_koya_zero_rounds_is_zero(self):
        p = PlayerTiebreakData(1, 1500, 2.0, [rec(2, 1.0)])
        allp = {1: p, 2: PlayerTiebreakData(2, 1500, 2.0, [])}
        assert calculate(p, allp, "koya", total_rounds=0) == 0.0
