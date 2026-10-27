"""REP (§7.6) forfeit/bye scope — Swiss and round-robin, all round kinds.

Regression for the ``rounds_played_elected`` defect: round-robin REP
excluded only requested byes, so forfeit losses counted as elected
rounds, contradicting §7.6 ("the number of rounds reduced by the number
of half-point-byes, zero-point-byes or forfeit losses") and §15.2
("forfeit losses in Type B tie-breaks … remain unplayed rounds").

§7.6 is mode-independent, so Swiss and round-robin REP must agree for
every round classification. The fixtures below hand-compute every
expected value from the recorded rounds.

Type scope (checked here so the REP fix is not mistaken for a general
forfeit change):

* Type B (WIN/WON/BPG/BWG) — forfeit losses excluded, forfeit wins
  counted (§15.2 carve-out; §7.1–7.4 "over the board").
* Type C (BH/SB) — forfeits count as regular games in round-robins.
* Type A (DE) — forfeits excluded in Swiss, included in round-robins.
"""
import itertools

import pytest

from tiebreak_core import fide2026 as f26
from tiebreak_core.errors import InvalidPlayerDataError
from tiebreak_core.models import GameRecord as G
from tiebreak_core.models import PlayerTiebreakData as P


def _swiss_fixture():
    """4 players, 4 rounds: HPB, PAB, forfeit loss, forfeit win.

    R1 P1-P2 (P1 wins), P3-P4 (P3 wins)
    R2 P1-P3 (draw), P2-P4 (P2 wins)
    R3 P1 HPB, P2-P3 (draw), P4 PAB
    R4 P1-P2 (P1 forfeit win), P3-P4 (P3 wins)

    Scores: P1 3.0, P2 1.5, P3 3.0, P4 1.0 (8.5 total).
    """
    return {
        1: P(1, 2000, 3.0, [G(2, 0, 1.0, "white", 1, "played"),
                            G(3, 0, 0.5, "white", 2, "played"),
                            G(-1, 0, 0.5, "white", 3, "requested_bye"),
                            G(2, 0, 1.0, "white", 4, "played")]),
        2: P(2, 1900, 1.5, [G(1, 0, 0.0, "black", 1, "played"),
                            G(4, 0, 1.0, "white", 2, "played"),
                            G(3, 0, 0.5, "white", 3, "played"),
                            G(1, 0, 0.0, "black", 4, "forfeit_loss")]),
        3: P(3, 1800, 3.0, [G(4, 0, 1.0, "white", 1, "played"),
                            G(1, 0, 0.5, "black", 2, "played"),
                            G(2, 0, 0.5, "black", 3, "played"),
                            G(4, 0, 1.0, "white", 4, "played")]),
        4: P(4, 1700, 1.0, [G(3, 0, 0.0, "black", 1, "played"),
                            G(2, 0, 0.0, "black", 2, "played"),
                            G(-1, 0, 1.0, "white", 3, "pairing_bye"),
                            G(3, 0, 0.0, "black", 4, "played")]),
    }


def _zero_point_bye_fixture():
    """3 players, 2 rounds: a zero-point bye (justified absence).

    R1 P1-P2 (P1 wins), P3 PAB; R2 P2-P3 (P2 wins), P1 ZPB.
    Scores 1.0 / 1.0 / 1.0.
    """
    return {
        1: P(1, 2000, 1.0, [G(2, 0, 1.0, "white", 1, "played"),
                            G(-1, 0, 0.0, "white", 2, "requested_bye")]),
        2: P(2, 1900, 1.0, [G(1, 0, 0.0, "black", 1, "played"),
                            G(3, 0, 1.0, "white", 2, "played")]),
        3: P(3, 1800, 1.0, [G(-1, 0, 1.0, "white", 1, "pairing_bye"),
                            G(2, 0, 0.0, "black", 2, "played")]),
    }


class TestSwissRepScope:
    """§7.6 Swiss: recorded non-absent rounds − §16.1.2 VURs."""

    def test_hpb_and_forfeit_loss_are_vur_pairing_bye_is_not(self):
        pl = _swiss_fixture()
        # P1: 4 rounds, R3 requested bye -> 3.0
        # P2: 4 rounds, R4 forfeit loss -> 3.0
        # P3: 4 rounds, no VUR -> 4.0
        # P4: 4 rounds, R3 pairing-allocated bye (not a VUR) -> 4.0
        got = {pid: f26.calculate(pl[pid], pl, "rounds_elected", 4, "swiss")
               for pid in pl}
        assert got == {1: 3.0, 2: 3.0, 3: 4.0, 4: 4.0}

    def test_zero_point_bye_is_a_vur(self):
        pl = _zero_point_bye_fixture()
        got = {pid: f26.calculate(pl[pid], pl, "rounds_elected", 2, "swiss")
               for pid in pl}
        # P1's ZPB reduces REP; P2 has none; P3's PAB does not.
        assert got == {1: 1.0, 2: 2.0, 3: 2.0}

    def test_all_rounds_unplayed_rep_is_zero(self):
        pl = {1: P(1, 2000, 1.0, [G(-1, 0, 0.5, "white", 1, "requested_bye"),
                                  G(-1, 0, 0.5, "white", 2, "requested_bye")])}
        assert f26.calculate(pl[1], pl, "rounds_elected", 2, "swiss") == 0.0

    def test_no_unplayed_rounds_rep_equals_rounds(self):
        pl = {1: P(1, 2000, 2.0, [G(2, 0, 1.0, "white", 1, "played"),
                                  G(2, 0, 1.0, "white", 2, "played")]),
              2: P(2, 1900, 0.0, [G(1, 0, 0.0, "black", 1, "played"),
                                  G(1, 0, 0.0, "black", 2, "played")])}
        for pid in pl:
            assert f26.calculate(pl[pid], pl, "rounds_elected", 2,
                                 "swiss") == 2.0

    def test_forfeit_without_scheduled_opponent_still_excluded(self):
        """A forfeit loss with no known opponent is still a §16.2.4 VUR."""
        pl = {1: P(1, 2000, 0.0, [G(-1, 0, 0.0, "white", 1, "forfeit_loss"),
                                  G(-1, 0, 0.0, "white", 2, "forfeit_loss")]),
              2: P(2, 1900, 1.0, [G(-1, 0, 1.0, "white", 1, "pairing_bye"),
                                  G(-1, 0, 1.0, "white", 2, "pairing_bye")])}
        assert f26.calculate(pl[1], pl, "rounds_elected", 2, "swiss") == 0.0


class TestRoundRobinRepScope:
    """§7.6 + §15.2 round-robin: requested byes and forfeit losses excluded."""

    def test_matches_swiss_for_every_round_classification(self):
        pl = _swiss_fixture()
        for pid in pl:
            rr = f26.calculate(pl[pid], pl, "rounds_elected", 4,
                               "round_robin")
            sw = f26.calculate(pl[pid], pl, "rounds_elected", 4, "swiss")
            assert rr == pytest.approx(sw)

    def test_zero_point_bye_fixture_agrees_with_swiss(self):
        pl = _zero_point_bye_fixture()
        for pid in pl:
            assert f26.calculate(pl[pid], pl, "rounds_elected", 2,
                                 "round_robin") == pytest.approx(
                    f26.calculate(pl[pid], pl, "rounds_elected", 2, "swiss"))

    def test_forfeit_loss_excluded_forfeit_win_elected(self):
        # #2 forfeit-loses R3 (black) and #1 forfeit-wins R3.
        pl = {
            1: P(1, 2000, 2.0, [G(2, 0, 1.0, "white", 1, "played"),
                                G(3, 0, 1.0, "white", 2, "forfeit_win")]),
            2: P(2, 1900, 0.0, [G(1, 0, 0.0, "black", 1, "played"),
                                G(3, 0, 0.0, "black", 2, "forfeit_loss")]),
            3: P(3, 1800, 1.0, [G(-1, 0, 1.0, "white", 1, "pairing_bye"),
                                G(2, 0, 1.0, "white", 2, "forfeit_win")]),
        }
        # #1: 2 rounds, no exclusion -> 2.0 (forfeit WIN stays elected)
        # #2: 2 rounds, R2 forfeit loss -> 1.0
        # #3: 2 rounds, no exclusion -> 2.0
        got = {pid: f26.calculate(pl[pid], pl, "rounds_elected", 2,
                                  "round_robin") for pid in pl}
        assert got == {1: 2.0, 2: 1.0, 3: 2.0}

    def test_property_over_forfeit_permutations(self):
        """Exhaustive over which rounds of a 4-round event are forfeits.

        For every assignment of {played, forfeit_win, forfeit_loss} to
        the four rounds of one player, Swiss and round-robin REP must
        agree, and each forfeit loss / requested bye must reduce REP by
        exactly one.
        """
        opp = {1: 2, 2: 3, 3: 4, 4: 1}
        kinds = ("played", "forfeit_win", "forfeit_loss")
        for combo in itertools.product(kinds, repeat=4):
            games = []
            for rnd, kind in enumerate(combo, start=1):
                games.append(G(opp[1], 0,
                               {"played": 1.0, "forfeit_win": 1.0,
                                "forfeit_loss": 0.0}[kind],
                               "white", rnd, kind))
            player = P(1, 2000, sum(g.score for g in games), games)
            others = {pid: P(pid, 1500, 1.0, [G(-1, 0, 1.0, "white", 1,
                                                "pairing_bye")])
                      for pid in (2, 3, 4)}
            players = {1: player, **others}
            rr = f26.calculate(player, players, "rounds_elected", 4,
                               "round_robin")
            sw = f26.calculate(player, players, "rounds_elected", 4, "swiss")
            assert rr == pytest.approx(sw)
            expected = 4 - sum(1 for k in combo
                               if k in ("forfeit_loss", "requested_bye"))
            assert rr == pytest.approx(expected)


def _type_b_fixture():
    """4 players, 3 rounds: a forfeit win (black) and a forfeit loss.

    #1: R1 played win vs #2 (white), R2 forfeit win vs #3 (black),
        R3 played draw vs #4 (white) -> 2.5
    #2: R1 played loss vs #1 (black), R2 played win vs #4 (white),
        R3 forfeit loss vs #3 (black) -> 1.0
    #3: R1 played win vs #4 (white), R2 forfeit loss vs #1 (white),
        R3 played draw vs #2 (white) -> 1.5
    #4: R1 played loss vs #3 (black), R2 played loss vs #2 (black),
        R3 played draw vs #1 (black) -> 0.5
    """
    return {
        1: P(1, 2000, 2.5, [G(2, 0, 1.0, "white", 1, "played"),
                            G(3, 0, 1.0, "black", 2, "forfeit_win"),
                            G(4, 0, 0.5, "white", 3, "played")]),
        2: P(2, 1900, 1.0, [G(1, 0, 0.0, "black", 1, "played"),
                            G(4, 0, 1.0, "white", 2, "played"),
                            G(3, 0, 0.0, "black", 3, "forfeit_loss")]),
        3: P(3, 1800, 1.5, [G(4, 0, 1.0, "white", 1, "played"),
                            G(1, 0, 0.0, "white", 2, "forfeit_loss"),
                            G(2, 0, 0.5, "white", 3, "played")]),
        4: P(4, 1700, 0.5, [G(3, 0, 0.0, "black", 1, "played"),
                            G(2, 0, 0.0, "black", 2, "played"),
                            G(1, 0, 0.5, "black", 3, "played")]),
    }


class TestRepTypeScope:
    """REP is one criterion; the same rounds must not perturb others."""

    def test_type_b_forfeit_win_counts_only_in_rr(self):
        """§7.2–7.4 "over the board": RR adds the scheduled forfeit win.

        #1's R2 is a forfeit win with Black. Swiss counts only played
        games (WON 1, BPG 0, BWG 0); round-robin counts it (§15.2)
        (WON 2, BPG 1, BWG 1).
        """
        pl = _type_b_fixture()
        assert f26.calculate(pl[1], pl, "won", 3, "swiss") == 1.0
        assert f26.calculate(pl[1], pl, "games_black", 3, "swiss") == 0.0
        assert f26.calculate(pl[1], pl, "wins_black", 3, "swiss") == 0.0
        assert f26.calculate(pl[1], pl, "won", 3, "round_robin") == 2.0
        assert f26.calculate(pl[1], pl, "games_black", 3,
                             "round_robin") == 1.0
        assert f26.calculate(pl[1], pl, "wins_black", 3,
                             "round_robin") == 1.0

    def test_type_b_forfeit_loss_excluded_in_both_modes(self):
        """§15.2: a forfeit LOSS is not an over-the-board game.

        #2's R3 is a forfeit loss with Black: it never enters WON, BPG
        or BWG in either regime.
        """
        pl = _type_b_fixture()
        for mode in ("swiss", "round_robin"):
            assert f26.calculate(pl[2], pl, "won", 3, mode) == 1.0
            assert f26.calculate(pl[2], pl, "games_black", 3, mode) == 1.0
            assert f26.calculate(pl[2], pl, "wins_black", 3, mode) == 0.0

    def test_wins_counts_forfeit_wins_in_both_modes(self):
        """§7.1 "with or without playing": WIN sees the awarded points."""
        pl = _type_b_fixture()
        for mode in ("swiss", "round_robin"):
            assert f26.calculate(pl[1], pl, "wins", 3, mode) == 2.0

    def test_type_c_forfeits_count_as_regular_in_rr(self):
        pl = _swiss_fixture()
        # #2's R4 forfeit loss vs #1 contributes adj(#1) = 3.0 in RR.
        rr = f26.calculate(pl[2], pl, "buchholz", 4, "round_robin")
        # R1 adj(1)=3.0, R2 adj(4)=1.0, R3 adj(3)=3.0, R4 adj(1)=3.0
        assert rr == pytest.approx(10.0)

    def test_type_a_de_excludes_forfeits_in_swiss(self):
        pl = {1: P(1, 2000, 2.0, [G(2, 0, 1.0, "white", 1, "forfeit_win")]),
              2: P(2, 1900, 2.0, [G(1, 0, 0.0, "black", 1, "forfeit_loss")])}
        rr = f26.rank_standings(pl, ["direct_encounter"], 1,
                                mode="round_robin")
        assert [p.player_id for p in rr.players] == [1, 2]
        sw = f26.rank_standings(pl, ["direct_encounter"], 1, mode="swiss",
                                deterministic_keys={1: 2, 2: 1})
        # Swiss excludes the forfeit pair, so the tie is unresolved.
        assert [p.player_id for p in sw.players] == [2, 1]

    def test_rep_unaffected_by_other_criteria(self):
        """Changing BH/SB must not move REP (no shared mutable state)."""
        pl = _swiss_fixture()
        before = {pid: f26.calculate(pl[pid], pl, "rounds_elected", 4,
                                     "round_robin") for pid in pl}
        f26.calculate(pl[1], pl, "buchholz", 4, "round_robin")
        f26.calculate(pl[2], pl, "sonneborn_berger", 4, "round_robin")
        after = {pid: f26.calculate(pl[pid], pl, "rounds_elected", 4,
                                    "round_robin") for pid in pl}
        assert before == after


class TestRepInputValidation:
    def test_dangling_opponent_record_rejected(self):
        """A played round referencing an absent opponent fails fast."""
        pl = {1: P(1, 2000, 0.0, [G(9, 0, 0.0, "white", 1, "played")]),
              2: P(2, 1900, 1.0, [G(-1, 0, 1.0, "white", 1, "pairing_bye")])}
        with pytest.raises(InvalidPlayerDataError):
            f26.calculate(pl[1], pl, "rounds_elected", 1, "round_robin")

    def test_absent_round_is_not_counted(self):
        """A gap in the record (no round entry) is not an elected round."""
        pl = {1: P(1, 2000, 1.0, [G(2, 0, 1.0, "white", 1, "played"),
                                  G(2, 0, 0.0, "white", 3, "played")]),
              2: P(2, 1900, 0.0, [G(1, 0, 0.0, "black", 1, "played"),
                                  G(1, 0, 0.0, "black", 3, "played")])}
        assert f26.calculate(pl[1], pl, "rounds_elected", 3, "swiss") == 2.0

    def test_total_rounds_must_be_positive(self):
        pl = _swiss_fixture()
        with pytest.raises(InvalidPlayerDataError):
            f26.calculate(pl[1], pl, "rounds_elected", 0, "round_robin")
