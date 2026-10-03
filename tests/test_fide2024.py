"""fide-2024 engine — Article 16 mechanics + criterion values.

The 5-round event below is hand-computed independently in full (see
corpus file ``fide2024_swiss5.json`` for the mirrored VERIFIED case).
Every number traces to the FIDE Council document 2024_FC2_18
(PRO primary source, retrieved in full).

Event (points: P1 3.5, P2 1.5, P3 4.5, P4 0.5):
  R1: P1-P2 1-0, P3-P4 1-0
  R2: P1 pairing-bye, P2-P3 0-1, P4 requested half-bye
  R3: P1-P3 0-1, P2-P4 1-0
  R4: P1 requested half-bye, P2-P3 draw, P4 requested zero-bye
  R5: P1-P4 1-0, P2 requested zero-bye (withdrawn), P3 pairing-bye
"""
import pytest

from tiebreak_core import (
    calculate_all_strict,
    rank_standings_strict,
    InvalidGameRecordError,
    InvalidPlayerDataError,
    UnknownCriterionError,
    UnsupportedCriterionError,
)
from tiebreak_core import fide2024 as fide
from tiebreak_core.models import GameRecord, PlayerTiebreakData


def g(opp, score, color="white", rnd=1, rating=1500, kind=""):
    return GameRecord(opponent_id=opp, opponent_rating=rating, score=score,
                      color=color, round_number=rnd, kind=kind)


def event():
    p1 = PlayerTiebreakData(1, 2000, 3.5, [
        g(2, 1.0, "white", 1, 1900, "played"),
        g(-1, 1.0, "white", 2, 0, "pairing_bye"),
        g(3, 0.0, "white", 3, 1800, "played"),
        g(-1, 0.5, "white", 4, 0, "requested_bye"),
        g(4, 1.0, "white", 5, 1700, "played"),
    ])
    p2 = PlayerTiebreakData(2, 1900, 1.5, [
        g(1, 0.0, "black", 1, 2000, "played"),
        g(3, 0.0, "white", 2, 1800, "played"),
        g(4, 1.0, "white", 3, 1700, "played"),
        g(3, 0.5, "black", 4, 1800, "played"),
        g(-1, 0.0, "white", 5, 0, "requested_bye"),
    ])
    p3 = PlayerTiebreakData(3, 1800, 4.5, [
        g(4, 1.0, "white", 1, 1700, "played"),
        g(2, 1.0, "black", 2, 1900, "played"),
        g(1, 1.0, "black", 3, 2000, "played"),
        g(2, 0.5, "white", 4, 1900, "played"),
        g(-1, 1.0, "white", 5, 0, "pairing_bye"),
    ])
    p4 = PlayerTiebreakData(4, 1700, 0.5, [
        g(3, 0.0, "black", 1, 1800, "played"),
        g(-1, 0.5, "white", 2, 0, "requested_bye"),
        g(2, 0.0, "black", 3, 1900, "played"),
        g(-1, 0.0, "white", 4, 0, "requested_bye"),
        g(1, 0.0, "black", 5, 2000, "played"),
    ])
    return {1: p1, 2: p2, 3: p3, 4: p4}


CRITERIA = ["buchholz", "buchholz_cut1", "buchholz_cut2",
            "median_buchholz", "median_buchholz_2",
            "sonneborn_berger", "sonneborn_berger_cut1",
            "progressive", "progressive_cut1", "koya",
            "aro", "aro_cut1", "aob", "fore_buchholz",
            "wins", "won", "games_black", "wins_black",
            "rounds_elected"]

EXPECTED = {
    1: {"buchholz": 14.0, "buchholz_cut1": 10.5, "buchholz_cut2": 10.0,
        "median_buchholz": 6.0, "median_buchholz_2": 2.0,
        "sonneborn_berger": 7.75, "sonneborn_berger_cut1": 6.0,
        "progressive": 11.0, "progressive_cut1": 10.0, "koya": 0.0,
        "aro": 1800, "aro_cut1": 1850, "aob": 12.7, "fore_buchholz": 13.5,
        "wins": 3.0, "won": 2.0, "games_black": 0.0, "wins_black": 0.0,
        "rounds_elected": 4.0},
    2: {"buchholz": 14.5, "buchholz_cut1": 13.0, "buchholz_cut2": 12.5,
        "median_buchholz": 8.5, "median_buchholz_2": 3.5,
        # P2 SB-C1 = 2.25 (corrected 0.9.0): products R1 0 (basis 3.5),
        # R2 0 (basis 4.5), R3 0.5 (basis 0.5), R4 2.25 (basis 4.5),
        # R5 VUR 0. §14.1.1.d cuts the product of the lowest-score
        # opponent (R3, 0.5); VUR-min 0 does not overrule. The former
        # 2.75 cut the least product (0) instead — wrong per 14.1.1.d.
        "sonneborn_berger": 2.75, "sonneborn_berger_cut1": 2.25,
        "progressive": 4.0, "progressive_cut1": 4.0, "koya": 0.5,
        "aro": 1825, "aro_cut1": 1867, "aob": 12.5, "fore_buchholz": 14.5,
        "wins": 1.0, "won": 1.0, "games_black": 2.0, "wins_black": 0.0,
        "rounds_elected": 4.0},
    3: {"buchholz": 12.5, "buchholz_cut1": 12.0, "buchholz_cut2": 10.0,
        "median_buchholz": 7.5, "median_buchholz_2": 2.0,
        "sonneborn_berger": 11.5, "sonneborn_berger_cut1": 11.0,
        "progressive": 14.0, "progressive_cut1": 13.0, "koya": 1.0,
        "aro": 1875, "aro_cut1": 1933, "aob": 13.5, "fore_buchholz": 12.5,
        "wins": 4.0, "won": 3.0, "games_black": 2.0, "wins_black": 2.0,
        "rounds_elected": 5.0},
    4: {"buchholz": 11.0, "buchholz_cut1": 10.5, "buchholz_cut2": 10.0,
        "median_buchholz": 6.0, "median_buchholz_2": 2.0,
        "sonneborn_berger": 0.25, "sonneborn_berger_cut1": 0.25,
        "progressive": 2.0, "progressive_cut1": 2.0, "koya": 0.0,
        "aro": 1900, "aro_cut1": 1950, "aob": 13.7, "fore_buchholz": 11.5,
        "wins": 0.0, "won": 0.0, "games_black": 3.0, "wins_black": 0.0,
        "rounds_elected": 3.0},
}


class TestClassification:
    def test_categories_and_vur(self):
        players = event()
        ctx1 = {r.round_number: (r.category, r.is_vur)
                for r in fide.classify(players[1])}
        assert ctx1[2] == ("16.2.1", False)   # pairing bye, not VUR
        assert ctx1[4] == ("16.2.3", True)    # early requested bye, VUR
        ctx2 = {r.round_number: (r.category, r.is_vur)
                for r in fide.classify(players[2])}
        assert ctx2[5] == ("16.2.5", True)    # trailing zero-bye, VUR
        ctx4 = {r.round_number: (r.category, r.is_vur)
                for r in fide.classify(players[4])}
        assert ctx4[2] == ("16.2.3", True)
        assert ctx4[4] == ("16.2.3", True)

    def test_adjusted_scores_16_3(self):
        players = event()
        ctx = {pid: fide.classify(p) for pid, p in players.items()}
        adj = {pid: fide.adjusted_score(ctx[pid]) for pid in players}
        # P2's trailing zero-bye counts as a draw for opponents' use.
        assert adj == {1: 3.5, 2: 2.0, 3: 4.5, 4: 0.5}


class TestValues:
    @pytest.mark.parametrize("pid", [1, 2, 3, 4])
    def test_full_event(self, pid):
        players = event()
        got = calculate_all_strict(players[pid], players, CRITERIA, 5,
                                   ruleset="fide-2024")
        for crit, want in EXPECTED[pid].items():
            assert got[crit] == pytest.approx(want), f"P{pid} {crit}"


class TestRanking:
    def test_order_and_stamp(self):
        players = event()
        res = rank_standings_strict(
            players, ["buchholz_cut1", "buchholz", "sonneborn_berger",
                      "progressive"], 5,
            deterministic_keys={1: 1, 2: 2, 3: 3, 4: 4},
            ruleset="fide-2024")
        assert res.rules_version == "fide-2024"
        # Points: P3 4.5 > P1 3.5 > P2 1.5 > P4 0.5.
        assert [p.player_id for p in res.players] == [3, 1, 2, 4]


class TestBoundaries:
    def test_uncategorized_sentinel_rejected(self):
        players = event()
        bad = PlayerTiebreakData(9, 1500, 1.0, [g(-1, 1.0, "white", 1)])
        with pytest.raises(InvalidGameRecordError):
            calculate_all_strict(bad, {**players, 9: bad}, ["buchholz"],
                                 5, ruleset="fide-2024")

    def test_zero_total_rounds_rejected(self):
        players = event()
        with pytest.raises(InvalidPlayerDataError):
            calculate_all_strict(players[1], players, ["buchholz"], 0,
                                 ruleset="fide-2024")

    def test_unimplemented_criteria_rejected(self):
        players = event()
        for crit in ("arpo", "buchholz_sum", "direct_encounter"):
            with pytest.raises(UnsupportedCriterionError):
                calculate_all_strict(players[1], players, [crit], 5,
                                     ruleset="fide-2024")

    def test_unknown_criterion_still_unknown(self):
        players = event()
        with pytest.raises(UnknownCriterionError):
            calculate_all_strict(players[1], players, ["nope"], 5,
                                 ruleset="fide-2024")

    def test_legacy_unaffected_by_kinds(self):
        # Same event under legacy: different (frozen) numbers — the two
        # rulesets are independent implementations.
        from tiebreak_core import calculate
        players = event()
        assert calculate(players[1], players, "buchholz") == 12.0

    def test_sb_c1_cuts_lowest_scored_opponent(self):
        # F1 discriminator (§14.1.1.d): win vs 2.0 (product 2.0) +
        # draw vs 3.0 (product 1.5). The least product is 1.5, but
        # the cut must remove the 2.0 (lowest-scored opponent).
        players = {
            1: PlayerTiebreakData(1, 2000, 1.5, [
                g(2, 1.0, "white", 1, 1900, "played"),
                g(3, 0.5, "black", 2, 1800, "played")]),
            2: PlayerTiebreakData(2, 1900, 2.0, [
                g(1, 0.0, "black", 1, 2000, "played"),
                g(9, 1.0, "white", 2, 0, "played"),
                g(9, 1.0, "white", 3, 0, "played")]),
            3: PlayerTiebreakData(3, 1800, 3.0, [
                g(1, 0.5, "white", 2, 2000, "played"),
                g(9, 1.0, "white", 1, 0, "played"),
                g(9, 1.0, "white", 3, 0, "played"),
                g(9, 0.5, "white", 4, 0, "played")]),
            9: PlayerTiebreakData(9, 1500, 0.0, []),
        }
        got = calculate_all_strict(players[1], players,
                                   ["sonneborn_berger",
                                    "sonneborn_berger_cut1"], 4,
                                   ruleset="fide-2024")
        assert got["sonneborn_berger"] == pytest.approx(3.5)
        assert got["sonneborn_berger_cut1"] == pytest.approx(1.5)


class TestRegistry:
    def test_fide_ids_supported(self):
        for cid in fide.FIDE2024_IDS:
            assert fide.is_supported_criterion(cid)

    def test_redefined_ids_documented(self):
        assert set(fide.REDEFINED_IDS) <= set(fide.FIDE2024_IDS)
