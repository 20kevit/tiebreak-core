"""fide-2026 engine (Phase F26-1): dummy caps, mode flag, terminals.

Covers §16.4.1/16.4.2 capped dummies, the swiss/round_robin mode flag
(§15.2 carve-out), TPN/RTNG terminal stages (§§7.8/10.6), Swiss parity
with fide-2024 on fully-played events, cap monotonicity (2026 ≤ 2024),
property/invariant tests, and adversarial edge cases.
"""
import copy
import random

import pytest

from tiebreak_core import fide2026 as f26
from tiebreak_core import fide2024 as f24
from tiebreak_core.errors import (
    InvalidPlayerDataError,
    UnknownCriterionError,
    UnsupportedCriterionError,
)
from tiebreak_core.models import GameRecord, PlayerTiebreakData


def P(pid, rating, points, games):
    return PlayerTiebreakData(
        player_id=pid, rating=rating, points=points,
        games=[GameRecord(opponent_id=o, opponent_rating=0, score=s,
                          color=c, round_number=r, kind=k)
               for (o, s, c, r, k) in games])


def swiss_event():
    """Small Swiss event with mixed unplayed rounds (coherent)."""
    return {
        1: P(1, 2000, 3.5, [(2, 1.0, "white", 1, "played"),
                             (-1, 1.0, "white", 2, "pairing_bye"),
                             (3, 1.0, "black", 3, "forfeit_win"),
                             (-1, 0.5, "white", 4, "requested_bye"),
                             (4, 0.0, "black", 5, "played")]),
        2: P(2, 1900, 1.0, [(1, 0.0, "black", 1, "played"),
                             (3, 0.5, "white", 2, "played"),
                             (4, 0.5, "black", 3, "played"),
                             (-1, 0.0, "white", 4, "requested_bye"),
                             (-1, 0.0, "white", 5, "requested_bye")]),
        3: P(3, 1800, 2.5, [(4, 1.0, "white", 1, "played"),
                             (2, 0.5, "black", 2, "played"),
                             (-1, 0.0, "white", 3, "forfeit_loss"),
                             (1, 1.0, "white", 4, "played"),
                             (-1, 0.0, "black", 5, "requested_bye")]),
        4: P(4, 1700, 2.0, [(3, 0.0, "black", 1, "played"),
                             (-1, 1.0, "white", 2, "pairing_bye"),
                             (1, 1.0, "white", 5, "played"),
                             (2, 0.0, "white", 4, "forfeit_loss"),
                             (-1, 0.0, "black", 3, "requested_bye")]),
    }


ALL_SCALARS = list(f26.FIDE2026_IDS)


class TestDummyCaps:
    def test_cap_16_4_2_pairing_bye(self):
        # Own 7.0, one pairing bye in 10 rounds: dummy min(7, 5) = 5.
        pl = {1: P(1, 2000, 7.0, [(2, 1.0, "white", r, "played")
                                  for r in range(1, 10)]
                  + [(-1, 1.0, "white", 10, "pairing_bye")]),
              2: P(2, 1500, 0.0, [])}
        assert f26.calculate(pl[1], pl, "buchholz", 10) == 5.0

    def test_cap_16_4_1_forfeit_win(self):
        # Scheduled opponent adjusted 1.5 < own 4.0: dummy = 1.5.
        pl = {1: P(1, 2000, 4.0, [(2, 1.0, "white", 1, "played"),
                                  (3, 1.0, "black", 2, "forfeit_win"),
                                  (2, 1.0, "white", 3, "played"),
                                  (2, 1.0, "black", 4, "played")]),
              2: P(2, 1500, 3.0, [(1, 0.0, "black", 1, "played"),
                                   (1, 0.0, "white", 3, "played"),
                                   (1, 0.0, "white", 4, "played"),
                                   (3, 1.0, "black", 2, "played"),
                                   (-1, 1.0, "white", 5, "pairing_bye")]),
              3: P(3, 1500, 1.5, [(2, 0.0, "white", 2, "played"),
                                   (2, 0.5, "black", 5, "played"),
                                   (-1, 1.0, "white", 1, "pairing_bye")])}
        # adj(3) = 0 + 0.5 + 1.0 = 1.5 -> R2 dummy min(4.0, 1.5).
        assert f26.calculate(pl[1], pl, "buchholz", 5) == \
            f24.calculate(pl[1], pl, "buchholz", 5) - 4.0 + 1.5

    def test_cap_16_4_1_forfeit_loss(self):
        pl = {1: P(1, 2000, 3.0, [(2, 1.0, "white", 1, "played"),
                                   (3, 0.0, "black", 2, "forfeit_loss"),
                                   (2, 1.0, "white", 3, "played"),
                                   (2, 1.0, "black", 4, "played")]),
              2: P(2, 1500, 1.0, [(1, 0.0, "black", 1, "played"),
                                   (1, 0.0, "white", 3, "played"),
                                   (1, 0.0, "white", 4, "played")]),
              3: P(3, 1500, 5.0, [(2, 1.0, "white", 1, "played"),
                                   (2, 1.0, "black", 2, "played"),
                                   (2, 1.0, "white", 3, "played"),
                                   (2, 1.0, "black", 4, "played"),
                                   (-1, 1.0, "white", 5, "pairing_bye")])}
        # adj(3) = 5+1 = 6.0 (R5 pairing bye counts awarded) ->
        # R2 dummy min(3.0, 6.0) = 3.0 (cap does not bind).
        assert f26.calculate(pl[1], pl, "buchholz", 5) == \
            f24.calculate(pl[1], pl, "buchholz", 5)

    def test_cap_unknown_scheduled_opponent_falls_back(self):
        # Forfeit vs unknown pairing (-1): no cap basis -> own score.
        pl = {1: P(1, 2000, 2.0, [(2, 1.0, "white", 1, "played"),
                                   (-1, 1.0, "black", 2, "forfeit_win"),
                                   (2, 0.0, "white", 3, "played")]),
              2: P(2, 1500, 1.0, [(1, 0.0, "black", 1, "played"),
                                   (1, 1.0, "black", 3, "played")])}
        assert f26.calculate(pl[1], pl, "buchholz", 3) == \
            f24.calculate(pl[1], pl, "buchholz", 3)

    def test_custom_draw_points(self):
        pl = {1: P(1, 2000, 7.0, [(2, 1.0, "white", r, "played")
                                  for r in range(1, 10)]
                  + [(-1, 1.0, "white", 10, "pairing_bye")]),
              2: P(2, 1500, 0.0, [])}
        assert f26.calculate(pl[1], pl, "buchholz", 10,
                             "swiss", 1.0) == 7.0  # exotic 3-1-0 draw
        with pytest.raises(InvalidPlayerDataError):
            f26.calculate(pl[1], pl, "buchholz", 10, "swiss", -0.5)

    def test_sb_dummy_uses_capped_value(self):
        # Forfeit win (score 1.0) contributes capped dummy x 1.0.
        pl = {1: P(1, 2000, 4.0, [(2, 1.0, "white", 1, "played"),
                                  (3, 1.0, "black", 2, "forfeit_win")]),
              2: P(2, 1500, 0.0, [(1, 0.0, "black", 1, "played")]),
              3: P(3, 1500, 1.0, [(2, 1.0, "white", 1, "played")])}
        # adj(2)=0, adj(3)=1.0 -> SB = 0*1 + 1.0*1 = 1.0
        assert f26.calculate(pl[1], pl, "sonneborn_berger", 2) == 1.0

    def test_fore_buchholz_applies_caps(self):
        pl = swiss_event()
        for pid in pl:
            assert f26.calculate(pl[pid], pl, "fore_buchholz", 5) <= \
                f24.calculate(pl[pid], pl, "fore_buchholz", 5)


class TestSwissParity:
    def test_fully_played_parity_all_scalars(self):
        pl = {
            1: P(1, 2000, 2.5, [(2, 1.0, "white", 1, "played"),
                                 (3, 0.5, "black", 2, "played"),
                                 (4, 1.0, "white", 3, "played")]),
            2: P(2, 1900, 1.0, [(1, 0.0, "black", 1, "played"),
                                 (4, 0.5, "white", 2, "played"),
                                 (3, 0.5, "black", 3, "played")]),
            3: P(3, 1800, 1.5, [(4, 0.5, "white", 1, "played"),
                                 (1, 0.5, "white", 2, "played"),
                                 (2, 0.5, "white", 3, "played")]),
            4: P(4, 1700, 1.0, [(3, 0.5, "black", 1, "played"),
                                 (2, 0.5, "black", 2, "played"),
                                 (1, 0.0, "black", 3, "played")]),
        }
        for pid in pl:
            for crit in ALL_SCALARS:
                if crit not in f24.FIDE2024_REGISTRY:
                    continue  # F26-2 C2/FB-combos have no 2024 counterpart
                assert f26.calculate(pl[pid], pl, crit, 3) == \
                    f24.calculate(pl[pid], pl, crit, 3), (pid, crit)

    def test_fully_played_ranking_parity(self):
        pl = {
            1: P(1, 2000, 2.0, [(2, 1.0, "white", 1, "played"),
                                 (3, 0.5, "black", 2, "played"),
                                 (4, 0.5, "white", 3, "played")]),
            2: P(2, 1900, 2.0, [(1, 0.0, "black", 1, "played"),
                                 (4, 1.0, "white", 2, "played"),
                                 (3, 1.0, "black", 3, "played")]),
            3: P(3, 1800, 1.0, [(4, 0.5, "white", 1, "played"),
                                 (1, 0.5, "white", 2, "played"),
                                 (2, 0.0, "white", 3, "played")]),
            4: P(4, 1700, 1.0, [(3, 0.5, "black", 1, "played"),
                                 (2, 0.0, "black", 2, "played"),
                                 (1, 0.5, "black", 3, "played")]),
        }
        crits = ["buchholz", "direct_encounter", "sonneborn_berger",
                 "progressive"]
        r24 = f24.rank_standings(pl, crits, 3)
        r26 = f26.rank_standings(pl, crits, 3)
        assert [p.player_id for p in r26.players] == \
               [p.player_id for p in r24.players]
        assert r26.rules_version == "fide-2026"

    def test_dangling_opponent_rejected_typed(self):
        from tiebreak_core.errors import InvalidPlayerDataError
        pl = {1: P(1, 2000, 1.0, [(99, 1.0, "white", 1, "played")])}
        with pytest.raises(InvalidPlayerDataError):
            f26.calculate(pl[1], pl, "buchholz", 1)
        with pytest.raises(InvalidPlayerDataError):
            f24.rank_standings(pl, ["buchholz"], 1)

    def test_cap_monotonicity_random_swiss(self):
        rng = random.Random(20260301)
        for trial in range(30):
            n, rounds = 8, 5
            pl = {}
            for pid in range(1, n + 1):
                games, pts = [], 0.0
                for r in range(1, rounds + 1):
                    roll = rng.random()
                    opp = (pid + r) % n + 1
                    if roll < 0.7:
                        s = rng.choice([0.0, 0.5, 1.0])
                        games.append((opp, s, "white", r, "played"))
                        pts += s
                    elif roll < 0.8:
                        games.append((-1, 1.0, "white", r, "pairing_bye"))
                        pts += 1.0
                    elif roll < 0.9:
                        games.append((opp, 1.0, "white", r, "forfeit_win"))
                        pts += 1.0
                    else:
                        games.append((-1, 0.0, "white", r, "requested_bye"))
                pl[pid] = P(pid, 1500, pts, games)
            for pid in pl:
                # Uncut sums only: caps lower every dummy element, so
                # 2026 <= 2024 element-wise. Cut/median variants are
                # excluded: capped dummies can change WHICH element is
                # cut (selection effect), so no ordering theorem holds
                # there — cuts are pinned by hand-derived + TEC cases.
                for crit in ("buchholz", "sonneborn_berger",
                             "fore_buchholz", "aob"):
                    assert f26.calculate(pl[pid], pl, crit, rounds) <= \
                        f24.calculate(pl[pid], pl, crit, rounds), \
                        (trial, pid, crit)


class TestRoundRobinMode:
    def rr_event(self):
        # 4-player RR with a forfeit: 1 forfeit-wins vs 3, 2 forfeit-loses.
        return {
            1: P(1, 2000, 2.5, [(2, 1.0, "white", 1, "played"),
                                 (3, 1.0, "black", 2, "forfeit_win"),
                                 (4, 0.5, "white", 3, "played")]),
            2: P(2, 1900, 1.0, [(1, 0.0, "black", 1, "played"),
                                 (4, 1.0, "white", 2, "played"),
                                 (3, 0.0, "black", 3, "forfeit_loss")]),
            3: P(3, 1800, 1.5, [(4, 1.0, "white", 1, "played"),
                                 (1, 0.0, "white", 2, "forfeit_loss"),
                                 (2, 0.5, "white", 3, "played")]),
            4: P(4, 1700, 0.5, [(3, 0.0, "black", 1, "played"),
                                 (2, 0.0, "black", 2, "played"),
                                 (1, 0.5, "black", 3, "played")]),
        }

    def test_invalid_mode_rejected(self):
        pl = self.rr_event()
        with pytest.raises(InvalidPlayerDataError):
            f26.calculate(pl[1], pl, "buchholz", 3, "knockout")

    def test_forfeit_counts_as_regular_for_buchholz(self):
        pl = self.rr_event()
        # RR: R2 forfeit win vs #3 contributes adj(3)=1.5, not a dummy.
        assert f26.calculate(pl[1], pl, "buchholz", 3, "round_robin") == \
            1.0 + 1.5 + 0.5

    def test_forfeit_loss_excluded_from_type_b(self):
        pl = self.rr_event()
        # #2's forfeit loss (black) is not a game with black in RR.
        assert f26.calculate(pl[2], pl, "games_black", 3,
                             "round_robin") == 1.0
        # ... nor in Swiss (OTB only).
        assert f26.calculate(pl[2], pl, "games_black", 3, "swiss") == 1.0

    def test_forfeit_win_counts_in_type_b_rr(self):
        pl = self.rr_event()
        # #1's forfeit win with black counts as won-with-black in RR...
        assert f26.calculate(pl[1], pl, "wins_black", 3,
                             "round_robin") == 1.0
        # ... but not in Swiss (not over the board).
        assert f26.calculate(pl[1], pl, "wins_black", 3, "swiss") == 0.0

    def test_rating_sets_exclude_forfeits_both_modes(self):
        pl = self.rr_event()
        for mode in ("swiss", "round_robin"):
            # #1 rated OTB opponents: #2 (1900), #4 (1700) only.
            assert f26.calculate(pl[1], pl, "aro", 3, mode) == 1800

    def test_koya_counts_rr_forfeits(self):
        pl = self.rr_event()
        # Threshold 1.5: #3 (1.5) qualifies; #1 scored 1.0 vs #3.
        assert f26.calculate(pl[1], pl, "koya", 3, "round_robin") == 1.0
        # Swiss: forfeit games are unplayed -> excluded.
        assert f26.calculate(pl[1], pl, "koya", 3, "swiss") == 0.0

    def test_rr_de_includes_forfeits(self):
        pl = self.rr_event()
        res = f26.rank_standings(
            {1: P(1, 2000, 2.0, [(2, 1.0, "white", 1, "forfeit_win")]),
             2: P(2, 1900, 2.0, [(1, 0.0, "black", 1, "forfeit_loss")])},
            ["direct_encounter"], 1, mode="round_robin")
        assert [p.player_id for p in res.players] == [1, 2]
        res_swiss = f26.rank_standings(
            {1: P(1, 2000, 2.0, [(2, 1.0, "white", 1, "forfeit_win")]),
             2: P(2, 1900, 2.0, [(1, 0.0, "black", 1, "forfeit_loss")])},
            ["direct_encounter"], 1, mode="swiss",
            deterministic_keys={1: 2, 2: 1})
        # Swiss excludes the forfeit pair -> unresolvable -> fallback.
        assert [p.player_id for p in res_swiss.players] == [2, 1]


class TestForfeitInclusionFlag:
    """MTB26 /P opt-in: Swiss regulations may count scheduled forfeits
    as played (cf. §6.1.1). Scope: BH/SB/FB/Koya + DE mini-table;
    Type-B and rating sets are unaffected (documented)."""

    def test_p_flag_matches_rr_for_buchholz(self):
        pl = TestRoundRobinMode().rr_event()
        swiss_p = f26.calculate(pl[1], pl, "buchholz", 3, "swiss", 0.5,
                                True)
        rr = f26.calculate(pl[1], pl, "buchholz", 3, "round_robin")
        assert swiss_p == rr == 3.0

    def test_p_flag_leaves_type_b_untouched(self):
        pl = TestRoundRobinMode().rr_event()
        assert f26.calculate(pl[1], pl, "wins_black", 3, "swiss", 0.5,
                             True) == 0.0  # still OTB-only
        assert f26.calculate(pl[2], pl, "games_black", 3, "swiss", 0.5,
                             True) == 1.0

    def test_p_flag_leaves_ratings_untouched(self):
        pl = TestRoundRobinMode().rr_event()
        assert f26.calculate(pl[1], pl, "aro", 3, "swiss", 0.5,
                             True) == 1800

    def test_p_flag_rejects_non_bool(self):
        pl = TestRoundRobinMode().rr_event()
        with pytest.raises(InvalidPlayerDataError):
            f26.calculate(pl[1], pl, "buchholz", 3, "swiss", 0.5, 1)

    def test_p_flag_rejected_outside_2026(self):
        from tiebreak_core import calculate_strict
        pl = TestRoundRobinMode().rr_event()
        with pytest.raises(InvalidPlayerDataError):
            calculate_strict(pl[1], pl, "buchholz", 3,
                             ruleset="fide-2024",
                             forfeits_as_played=True)

    def test_p_flag_strict_roundtrip(self):
        from tiebreak_core import rank_standings_strict
        pl = TestRoundRobinMode().rr_event()
        res = rank_standings_strict(pl, ["buchholz"], 3,
                                    ruleset="fide-2026",
                                    forfeits_as_played=True)
        assert res.rules_version == "fide-2026"
        res_rr = rank_standings_strict(pl, ["buchholz"], 3,
                                       ruleset="fide-2026",
                                       mode="round_robin")
        assert ([p.player_id for p in res.players]
                == [p.player_id for p in res_rr.players])


class TestSbCutIdentification:
    """F1 discriminators (§14.1.1.d): cuts follow the lowest-SCORED
    opponent, never the least product.

    Fixture: win vs 2.0 (product 2.0) + draw vs 3.0 (product 1.5).
    The least product (1.5) must survive; the 2.0 is cut.
    """

    def fixture(self):
        return {
            1: P(1, 2000, 1.5, [(2, 1.0, "white", 1, "played"),
                                 (3, 0.5, "black", 2, "played")]),
            2: P(2, 1500, 2.0, [(1, 0.0, "black", 1, "played"),
                                 (9, 1.0, "white", 2, "played"),
                                 (9, 1.0, "white", 3, "played")]),
            3: P(3, 1500, 3.0, [(1, 0.5, "white", 2, "played"),
                                 (9, 1.0, "white", 1, "played"),
                                 (9, 1.0, "white", 3, "played"),
                                 (9, 0.5, "white", 4, "played")]),
            9: P(9, 0, 0.0, []),
        }

    def test_sb_c1_cuts_lowest_scored_opponent(self):
        from tiebreak_core import calculate_all_strict
        pl = self.fixture()
        got = calculate_all_strict(pl[1], pl,
                                   ["sonneborn_berger",
                                    "sonneborn_berger_cut1"], 4,
                                   ruleset="fide-2026")
        assert got["sonneborn_berger"] == 3.5
        assert got["sonneborn_berger_cut1"] == 1.5

    def test_sb_c2_reapplies_opponent_score_cut(self):
        from tiebreak_core import calculate_all_strict
        # R1 win vs 4.0 (4.0), R2 loss vs 5.0 (0.0), R3 draw vs 1.0
        # (0.5). C1 cuts R3 (lowest basis 1.0) -> 4.0; C2 reapplies
        # (lowest remaining basis 4.0) -> 0.0. Least-product logic
        # would cut 0.0 first and keep 4.5/4.0 instead.
        pl = {
            1: P(1, 2000, 1.5, [(2, 1.0, "white", 1, "played"),
                                 (3, 0.0, "black", 2, "played"),
                                 (4, 0.5, "white", 3, "played")]),
            2: P(2, 1500, 4.0, [(1, 0.0, "black", 1, "played"),
                                 (9, 1.0, "white", 2, "played"),
                                 (9, 1.0, "white", 3, "played"),
                                 (9, 1.0, "white", 4, "played"),
                                 (9, 1.0, "white", 5, "played")]),
            3: P(3, 1500, 5.0, [(1, 1.0, "white", 2, "played"),
                                 (9, 1.0, "black", 1, "played"),
                                 (9, 1.0, "black", 3, "played"),
                                 (9, 1.0, "black", 4, "played"),
                                 (9, 1.0, "black", 5, "played")]),
            4: P(4, 1500, 1.0, [(1, 0.5, "black", 3, "played"),
                                 (9, 0.5, "white", 1, "played")]),
            9: P(9, 0, 0.0, []),
        }
        got = calculate_all_strict(pl[1], pl,
                                   ["sonneborn_berger",
                                    "sonneborn_berger_cut1",
                                    "sonneborn_berger_cut2"], 5,
                                   ruleset="fide-2026")
        assert got == {"sonneborn_berger": 4.5,
                       "sonneborn_berger_cut1": 4.0,
                       "sonneborn_berger_cut2": 0.0}


class TestCutCombosAndAobFb:
    """F26-2 MTB26 combos: SB-C2, ARO-C2, FB-C1/C2, AOB/FB.

    Hand-computed fixture (derivation in comments): P1 (3.5) meets
    O1..O4 (4.0/3.5/2.0/1.5) then takes a trailing requested half-bye
    (16.2.5, VUR; 16.4.2 cap min(3.5, 2.5) = 2.5). R5 is the final
    round: played finals project to draws in FB legs; the unpaired
    R5 bye keeps its awarded 0.5.
    """

    def fixture(self):
        return {
            1: P(1, 2000, 3.5, [
                (11, 1.0, "white", 1, "played"),
                (12, 0.5, "black", 2, "played"),
                (13, 1.0, "white", 3, "played"),
                (14, 0.5, "black", 4, "played"),
                (-1, 0.5, "white", 5, "requested_bye")]),
            11: P(11, 1800, 4.0, [
                (1, 0.0, "black", 1, "played"),
                (9999, 1.0, "white", 2, "played"),
                (9999, 1.0, "white", 3, "played"),
                (9999, 1.0, "white", 4, "played"),
                (9999, 1.0, "white", 5, "played")]),
            12: P(12, 1700, 3.5, [
                (9999, 1.0, "white", 1, "played"),
                (1, 0.5, "white", 2, "played"),
                (9999, 1.0, "white", 3, "played"),
                (9999, 1.0, "white", 4, "played"),
                (9999, 0.0, "white", 5, "played")]),
            13: P(13, 1600, 2.0, [
                (9999, 1.0, "white", 1, "played"),
                (9999, 0.0, "white", 2, "played"),
                (1, 0.0, "black", 3, "played"),
                (9999, 1.0, "white", 4, "played"),
                (9999, 0.0, "white", 5, "played")]),
            14: P(14, 1500, 1.5, [
                (9999, 0.0, "white", 1, "played"),
                (9999, 1.0, "white", 2, "played"),
                (9999, 0.0, "white", 3, "played"),
                (1, 0.5, "black", 4, "played"),
                (9999, 0.0, "white", 5, "played")]),
            9999: P(9999, 0, 0.0, []),
        }

    def test_fb_family(self):
        from tiebreak_core import calculate_all_strict
        pl = self.fixture()
        got = calculate_all_strict(
            pl[1], pl, ["buchholz", "fore_buchholz",
                        "fore_buchholz_cut1", "fore_buchholz_cut2",
                        "aob", "aob_fb"], 5, ruleset="fide-2026")
        # BH legs 4.0/3.5/2.0/1.5 + capped R5 dummy 2.5 = 13.5.
        # FB legs 3.5/4.0/2.5/2.0 (finals as draws) + 2.5 = 14.5;
        # C1 cuts the VUR 2.5 -> 12.0; C2 then cuts 2.0 -> 10.0.
        # AOB averages BH (4 x 3.5); AOB/FB averages FB (4 x 3.5).
        assert got == {"buchholz": 13.5, "fore_buchholz": 14.5,
                       "fore_buchholz_cut1": 12.0,
                       "fore_buchholz_cut2": 10.0, "aob": 3.5,
                       "aob_fb": 3.5}

    def test_sb_c2(self):
        from tiebreak_core import calculate_all_strict
        pl = self.fixture()
        got = calculate_all_strict(
            pl[1], pl, ["sonneborn_berger", "sonneborn_berger_cut1",
                        "sonneborn_berger_cut2"], 5, ruleset="fide-2026")
        # Elements [4.0, 1.75, 2.0, 0.75, 1.25(VUR)]: SB = 9.75;
        # C1 cuts higher-of(1.25, 0.75) = 1.25 -> 8.5; C2 reapplied
        # cuts 0.75 -> 7.75.
        assert got == {"sonneborn_berger": 9.75,
                       "sonneborn_berger_cut1": 8.5,
                       "sonneborn_berger_cut2": 7.75}

    def test_aro_c2(self):
        from tiebreak_core import calculate_all_strict
        pl = self.fixture()
        got = calculate_all_strict(
            pl[1], pl, ["aro", "aro_cut1", "aro_cut2"], 5,
            ruleset="fide-2026")
        assert got == {"aro": 1650.0, "aro_cut1": 1700.0,
                       "aro_cut2": 1750.0}

    def test_aro_c2_edge_uncut(self):
        pl = {1: P(1, 2000, 1.0, [(2, 1.0, "white", 1, "played")]),
              2: P(2, 1500, 0.0, [(1, 0.0, "black", 1, "played")])}
        # One rated OTB opponent (< 3): uncut ARO, documented edge.
        assert f26.calculate(pl[1], pl, "aro_cut2", 1) == 1500.0

    def test_c2_monotonicity_random_swiss(self):
        rng = random.Random(20260302)
        for trial in range(10):
            n, rounds = 8, 5
            pl = {}
            for pid in range(1, n + 1):
                games, pts = [], 0.0
                for r in range(1, rounds + 1):
                    roll = rng.random()
                    opp = (pid + r) % n + 1
                    if roll < 0.8:
                        s = rng.choice([0.0, 0.5, 1.0])
                        games.append((opp, s, "white", r, "played"))
                        pts += s
                    else:
                        games.append((-1, 0.5, "white", r,
                                      "requested_bye"))
                        pts += 0.5
                pl[pid] = P(pid, rng.choice([1200, 1500, 1800, 2100,
                                             2400]), pts, games)
            for pid in pl:
                # Subtractive families shrink along the cut chain
                # (elements are non-negative).
                sb = f26.calculate(pl[pid], pl, "sonneborn_berger",
                                   rounds)
                c1 = f26.calculate(pl[pid], pl, "sonneborn_berger_cut1",
                                   rounds)
                c2 = f26.calculate(pl[pid], pl, "sonneborn_berger_cut2",
                                   rounds)
                assert sb >= c1 >= c2, (trial, pid)
                fb = f26.calculate(pl[pid], pl, "fore_buchholz", rounds)
                fc1 = f26.calculate(pl[pid], pl, "fore_buchholz_cut1",
                                    rounds)
                fc2 = f26.calculate(pl[pid], pl, "fore_buchholz_cut2",
                                    rounds)
                assert fb >= fc1 >= fc2, (trial, pid)
                # Averaging families grow along the cut chain
                # (lowest ratings are dropped).
                aro = f26.calculate(pl[pid], pl, "aro", rounds)
                ac1 = f26.calculate(pl[pid], pl, "aro_cut1", rounds)
                ac2 = f26.calculate(pl[pid], pl, "aro_cut2", rounds)
                assert aro <= ac1 <= ac2 or not pl[pid].games, \
                    (trial, pid)


class TestStandardPoints:
    """STD §7.7 (D5): outscore the scheduled opponent — or the draw
    value when unplayed — for 1, halves for ties.

    Hand-computed fixture: P1 (3.0) W/D/L vs O1..O3, pairing bye R4,
    requested half-bye R5. STD = 1 + 0.5 + 0 + 1 + 0.5 = 3.0.
    """

    def fixture(self, explicit=True):
        def g(o, s, r, k, opp_score=None):
            return GameRecord(opponent_id=o, opponent_rating=1500,
                              score=s, color="white", round_number=r,
                              kind=k, opponent_score=opp_score)
        es = (lambda v: v) if explicit else (lambda v: None)
        return {
            1: PlayerTiebreakData(
                player_id=1, rating=2000, points=3.0, games=[
                    g(11, 1.0, 1, "played", es(0.0)),
                    g(12, 0.5, 2, "played", es(0.5)),
                    g(13, 0.0, 3, "played", es(1.0)),
                    g(-1, 1.0, 4, "pairing_bye"),
                    g(-1, 0.5, 5, "requested_bye")]),
            11: P(11, 1500, 0.0, [(1, 0.0, "black", 1, "played")]),
            12: P(12, 1500, 0.5, [(1, 0.5, "black", 2, "played")]),
            13: P(13, 1500, 1.0, [(1, 1.0, "black", 3, "played")]),
        }

    def test_explicit_opponent_scores(self):
        from tiebreak_core import calculate_strict
        pl = self.fixture(explicit=True)
        assert calculate_strict(pl[1], pl, "std", 5,
                                ruleset="fide-2026") == 3.0

    def test_derived_standard_complement(self):
        from tiebreak_core import calculate_strict
        pl = self.fixture(explicit=False)
        assert calculate_strict(pl[1], pl, "std", 5,
                                ruleset="fide-2026") == 3.0

    def test_exotic_draw_requires_explicit(self):
        from tiebreak_core import calculate_strict
        pl = self.fixture(explicit=False)
        with pytest.raises(InvalidPlayerDataError):
            calculate_strict(pl[1], pl, "std", 5, ruleset="fide-2026",
                             draw_points=1.0)

    def test_exotic_draw_with_explicit(self):
        from tiebreak_core import calculate_strict
        pl = self.fixture(explicit=True)
        # Draw value 1.0: R4 bye 1.0 ties (0.5), R5 0.5 loses (0.0);
        # played legs unchanged (explicit opp scores).
        assert calculate_strict(pl[1], pl, "std", 5, ruleset="fide-2026",
                                draw_points=1.0) == 2.0

    def test_forfeit_scope_pin(self):
        # Swiss: forfeit loss is unplayed -> 0 vs draw 0.5 -> 0.0.
        # Swiss+/P: regular game with explicit opp 0.0 -> tie -> 0.5.
        def mk(opp_score=None):
            return {
            1: PlayerTiebreakData(
                player_id=1, rating=2000, points=1.0, games=[
                    GameRecord(opponent_id=2, opponent_rating=1500,
                               score=1.0, color="white", round_number=1,
                               kind="played"),
                    GameRecord(opponent_id=3, opponent_rating=1500,
                               score=0.0, color="black", round_number=2,
                               kind="forfeit_loss",
                               opponent_score=opp_score)]),
            2: P(2, 1500, 0.0, [(1, 0.0, "black", 1, "played")]),
            3: P(3, 1500, 1.0, []),
        }
        assert f26.calculate(mk()[1], mk(), "std", 2) == 1.0
        assert f26.calculate(mk(0.0)[1], mk(0.0), "std", 2, "swiss",
                             0.5, True) == 1.5

    def test_absent_rounds_skipped(self):
        pl = {1: PlayerTiebreakData(
            player_id=1, rating=2000, points=1.0, games=[
                GameRecord(opponent_id=2, opponent_rating=1500,
                           score=1.0, color="white", round_number=1,
                           kind="played"),
                GameRecord(opponent_id=-1, opponent_rating=0,
                           score=0.0, color="white", round_number=2,
                           kind="absent")]),
            2: P(2, 1500, 0.0, [(1, 0.0, "black", 1, "played")])}
        assert f26.calculate(pl[1], pl, "std", 2) == 1.0

    def test_std_ranking_descending(self):
        from tiebreak_core import rank_standings_strict
        pl = self.fixture(explicit=True)
        pl[13] = P(13, 1500, 1.0, [(1, 1.0, "black", 3, "played")])
        res = rank_standings_strict(pl, ["std"], 5, ruleset="fide-2026")
        assert res.rules_version == "fide-2026"
        assert [p.player_id for p in res.players][0] == 1

    def test_std_unknown_outside_2026(self):
        from tiebreak_core import calculate_strict
        from tiebreak_core.errors import UnknownCriterionError
        pl = self.fixture(explicit=True)
        with pytest.raises(UnknownCriterionError):
            calculate_strict(pl[1], pl, "std", 5, ruleset="fide-2024")


class TestAobExactRanking:
    """F3 discriminator (§8.2 states no rounding): two players whose
    exact AOB values differ but round to the same tenth.

    Player 2: 4 OTB opps with BHs [2.5, 2.0, 2.0, 2.0] -> exact 2.125.
    Player 1: 8 OTB opps with BHs [2.5, 2.0 x7] -> exact 2.0625.
    Both display 2.1, but exact ranking must put player 2 first
    (player 1 has the lower id, so a rounded tie would order [1, 2]).
    """

    def fixture(self):
        return {
            2: P(2, 1500, 2.0, [(21, 1.0, "white", 1, "played"),
                                 (22, 1.0, "black", 2, "played"),
                                 (23, 0.0, "white", 3, "played"),
                                 (24, 0.0, "black", 4, "played")]),
            21: P(21, 1500, 0.5, [(2, 0.0, "black", 1, "played"),
                                   (29, 0.5, "white", 2, "played")]),
            22: P(22, 1500, 0.0, [(2, 0.0, "white", 2, "played")]),
            23: P(23, 1500, 1.0, [(2, 1.0, "black", 3, "played")]),
            24: P(24, 1500, 1.0, [(2, 1.0, "white", 4, "played")]),
            29: P(29, 1500, 0.5, [(21, 0.5, "black", 2, "played")]),
            1: P(1, 1500, 2.0, [(11, 1.0, "white", 1, "played"),
                                 (12, 1.0, "black", 2, "played"),
                                 (13, 0.0, "white", 3, "played"),
                                 (14, 0.0, "black", 4, "played"),
                                 (15, 0.0, "white", 5, "played"),
                                 (16, 0.0, "black", 6, "played"),
                                 (17, 0.0, "white", 7, "played"),
                                 (18, 0.0, "black", 8, "played")]),
            11: P(11, 1500, 0.5, [(1, 0.0, "black", 1, "played"),
                                   (19, 0.5, "white", 2, "played")]),
            12: P(12, 1500, 0.0, [(1, 0.0, "white", 2, "played")]),
            13: P(13, 1500, 1.0, [(1, 1.0, "black", 3, "played")]),
            14: P(14, 1500, 1.0, [(1, 1.0, "white", 4, "played")]),
            15: P(15, 1500, 1.0, [(1, 1.0, "black", 5, "played")]),
            16: P(16, 1500, 1.0, [(1, 1.0, "white", 6, "played")]),
            17: P(17, 1500, 1.0, [(1, 1.0, "black", 7, "played")]),
            18: P(18, 1500, 1.0, [(1, 1.0, "white", 8, "played")]),
            19: P(19, 1500, 0.5, [(11, 0.5, "black", 2, "played")]),
        }

    def test_exact_values_and_shared_display(self):
        from tiebreak_core import calculate_strict
        pl = self.fixture()
        for ruleset in ("fide-2024", "fide-2026"):
            a = calculate_strict(pl[2], pl, "aob", 8, ruleset=ruleset)
            b = calculate_strict(pl[1], pl, "aob", 8, ruleset=ruleset)
            assert a == 2.125, (ruleset, a)
            assert b == 2.0625, (ruleset, b)
            assert round(a, 1) == round(b, 1) == 2.1

    def test_ranking_uses_exact_values(self):
        from tiebreak_core import rank_standings_strict
        pl = self.fixture()
        for ruleset in ("fide-2024", "fide-2026"):
            res = rank_standings_strict(pl, ["aob"], 8, ruleset=ruleset)
            order = [p.player_id for p in res.players]
            # Exact: player 2 (2.125) ahead of player 1 (2.0625).
            # Rounded 2.1/2.1 would tie and fall back to id order.
            assert order[0] == 2, (ruleset, order[:4])
            assert order[1] == 1, (ruleset, order[:4])

    def test_aob_fb_unchanged(self):
        # Out of scope guard: AOB/FB keeps its established behavior
        # (documented 1dp presentation value) — this mission changes
        # `aob` only.
        from tiebreak_core import calculate_strict
        pl = self.fixture()
        got = calculate_strict(pl[2], pl, "aob_fb", 8,
                               ruleset="fide-2026")
        assert got == round(got, 1)


class TestTerminals:
    def test_tpn_orders_ascending(self):
        pl = {1: P(1, 2200, 2.0, []), 2: P(2, 2300, 2.0, []),
              3: P(3, 2100, 2.0, [])}
        res = f26.rank_standings(pl, ["buchholz", "tpn"], 1,
                                 pairing_numbers={1: 30, 2: 7, 3: 15})
        assert [p.player_id for p in res.players] == [2, 3, 1]
        assert res.rules_version == "fide-2026"

    def test_rtng_orders_by_rating_descending(self):
        pl = {1: P(1, 2200, 2.0, []), 2: P(2, 2300, 2.0, []),
              3: P(3, 2100, 2.0, [])}
        res = f26.rank_standings(pl, ["buchholz", "rtng"], 1)
        assert [p.player_id for p in res.players] == [2, 1, 3]

    def test_tpn_requires_pairing_numbers(self):
        pl = {1: P(1, 2200, 2.0, [])}
        with pytest.raises(InvalidPlayerDataError):
            f26.rank_standings(pl, ["tpn"], 1)
        with pytest.raises(InvalidPlayerDataError):
            f26.rank_standings(pl, ["tpn"], 1,
                               pairing_numbers={2: 5})  # missing pid 1

    def test_terminal_scalar_refused(self):
        pl = {1: P(1, 2200, 2.0, [])}
        for term in ("tpn", "rtng"):
            with pytest.raises(UnsupportedCriterionError):
                f26.calculate(pl[1], pl, term, 1)

    def test_terminals_break_full_ties_deterministically(self):
        pl = {1: P(1, 2000, 1.0, []), 2: P(2, 2000, 1.0, [])}
        res = f26.rank_standings(pl, ["tpn"], 1,
                                 pairing_numbers={1: 2, 2: 1})
        assert [p.player_id for p in res.players] == [2, 1]
        assert res.players[0].values == {}


class TestUnsupported:
    def test_unknown_criterion(self):
        pl = {1: P(1, 2000, 1.0, [])}
        with pytest.raises(UnknownCriterionError):
            f26.calculate(pl[1], pl, "std_opt", 1)

    def test_std_is_supported_not_unknown(self):
        # 'std' (§7.7) is implemented under fide-2026 (F26-2c).
        assert f26.is_supported_criterion("std")

    def test_std_is_unsupported_not_unknown(self):
        # 'std' is not registered anywhere -> unknown. A *known*
        # non-2026 id (legacy-only extension) is unsupported:
        pl = {1: P(1, 2000, 1.0, [])}
        with pytest.raises(UnsupportedCriterionError):
            f26.calculate(pl[1], pl, "buchholz_sum", 1)

    def test_mode_flags_rejected_outside_2026(self):
        from tiebreak_core import calculate_strict
        pl = {1: P(1, 2000, 1.0, [])}
        with pytest.raises(InvalidPlayerDataError):
            calculate_strict(pl[1], pl, "buchholz", 0,
                             ruleset="fide-2024", mode="round_robin")


class TestProperties:
    def test_deterministic_repeat(self):
        pl = swiss_event()
        first = {pid: f26.calculate_all(pl[pid], pl, ALL_SCALARS, 5)
                 for pid in pl}
        second = {pid: f26.calculate_all(pl[pid], pl, ALL_SCALARS, 5)
                  for pid in pl}
        assert first == second

    def test_permutation_invariance_of_values(self):
        pl = swiss_event()
        reordered = dict(reversed(list(pl.items())))
        for pid in pl:
            assert f26.calculate_all(pl[pid], pl, ALL_SCALARS, 5) == \
                f26.calculate_all(reordered[pid], reordered, ALL_SCALARS,
                                  5)

    def test_no_input_mutation(self):
        pl = swiss_event()
        snapshot = copy.deepcopy(pl)
        f26.rank_standings(pl, ["buchholz", "direct_encounter",
                                "sonneborn_berger", "tpn"], 5,
                           pairing_numbers={i: 5 - i for i in pl})
        assert pl == snapshot

    def test_ranking_covers_everyone_exactly_once(self):
        pl = swiss_event()
        res = f26.rank_standings(pl, ["buchholz_cut1", "direct_encounter",
                                      "sonneborn_berger"], 5)
        ids = [p.player_id for p in res.players]
        assert sorted(ids) == sorted(pl)
        assert [p.rank for p in res.players] == list(range(1, len(pl) + 1))

    def test_adversarial_all_tied_terminates(self):
        # 12 players, all 1.0, no mutual games: DE cannot split.
        pl = {i: P(i, 1500, 1.0, []) for i in range(1, 13)}
        res = f26.rank_standings(
            pl, ["buchholz", "direct_encounter", "rtng"], 3,
            deterministic_keys={i: -i for i in pl})
        assert len(res.players) == 12

    def test_adversarial_large_de_group_terminates(self):
        # 30-player round robin, everybody draws everybody: one giant
        # tie, mini-table all equal -> single tier -> falls through.
        n = 30
        pl = {}
        for i in range(1, n + 1):
            games = [(j, 0.5, "white" if (i + j) % 2 else "black",
                      ((i + j) % 5) + 1, "played")
                     for j in range(1, n + 1) if j != i]
            pl[i] = P(i, 1500, (n - 1) * 0.5, games)
        res = f26.rank_standings(pl, ["direct_encounter", "rtng"], 5)
        assert len(res.players) == n
        assert [p.rank for p in res.players] == list(range(1, n + 1))

    def test_empty_and_singleton_groups(self):
        res = f26.rank_standings({1: P(1, 1500, 0.0, [])}, ["buchholz"],
                                 1)
        assert [p.player_id for p in res.players] == [1]
        assert res.players[0].rank == 1
