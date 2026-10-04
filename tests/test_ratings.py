"""Rating family §§10.1–10.5 (fide-2024, individual Swiss scope).

Basis: C.07 §10 (FIDE Council 2024_FC2_18, PRIMARY full text) for
definitions; FIDE Rating Regulations §8.1a (p→dp) and §8.1b (D→PD)
tables embedded from the official 2022 PDF (PRIMARY, full extraction,
101 + 51 entries verified).

Coherent 6-player event (points == recorded scores):
  R1: X-A (X W), Y-Z (Y W), B-C (B L)
  R2: X-B (draw), Y-A (Y W)
  R3: X-C (X L), A-Z (A W)
  R4: A-C (draw), B-Z (B W)
Points: X 1.5, Y 2.0, Z 0.0, A 1.5, B 1.5, C 2.5.

Hand-verified: TPR(X)=1800 (ARO 1800, p .50→dp 0); TPR(Y)=2450
(ARO 1650, p 1.00→dp 800); TPR(Z)=867 (ARO 1667, p 0→dp −800);
TPR(A)=1638 (ARO 1725, p .375→.38→dp −87); TPR(B)=1800; TPR(C)=2106
(ARO 1833, p .833→.83→dp 273). PTP(X)=1799 (R=1798 gives 1.49 < 1.5).
PTP(A/B/C) + APRO/APPO cross-verified by an independent brute-force
implementation (linear scan, separate table copies).
"""
import pytest

from tiebreak_core import calculate_all_strict
from tiebreak_core.models import GameRecord, PlayerTiebreakData


def g(opp, score, rnd=1, rating=1500):
    return GameRecord(opponent_id=opp, opponent_rating=rating, score=score,
                      color="white", round_number=rnd)


def event():
    x = PlayerTiebreakData(1, 2000, 1.5, [g(4, 1.0, 1, 1800),
                                          g(5, 0.5, 2, 1700),
                                          g(6, 0.0, 3, 1900)])
    y = PlayerTiebreakData(2, 1500, 2.0, [g(3, 1.0, 1, 1500),
                                          g(4, 1.0, 2, 1800)])
    z = PlayerTiebreakData(3, 1500, 0.0, [g(2, 0.0, 1, 1500),
                                          g(4, 0.0, 3, 1800),
                                          g(5, 0.0, 4, 1700)])
    a = PlayerTiebreakData(4, 1800, 1.5, [g(1, 0.0, 1, 2000),
                                          g(2, 0.0, 2, 1500),
                                          g(3, 1.0, 3, 1500),
                                          g(6, 0.5, 4, 1900)])
    b = PlayerTiebreakData(5, 1700, 1.5, [g(6, 0.0, 1, 1900),
                                          g(1, 0.5, 2, 2000),
                                          g(3, 1.0, 4, 1500)])
    c = PlayerTiebreakData(6, 1900, 2.5, [g(5, 1.0, 1, 1700),
                                          g(1, 1.0, 3, 2000),
                                          g(4, 0.5, 4, 1800)])
    return {1: x, 2: y, 3: z, 4: a, 5: b, 6: c}


CRITERIA = ["tpr", "ptp", "apro", "appo"]

EXPECTED = {
    1: {"tpr": 1800.0, "ptp": 1799.0, "apro": 1848.0, "appo": 1848.0},
    2: {"tpr": 2450.0},
    3: {"tpr": 867.0},
    4: {"tpr": 1638.0, "ptp": 1599.0},
    5: {"tpr": 1800.0, "ptp": 1812.0},
    6: {"tpr": 2106.0, "ptp": 2133.0},
}


class TestRatingFamily:
    @pytest.mark.parametrize("pid", [1, 2, 3, 4, 5, 6])
    def test_values(self, pid):
        players = event()
        crit = [c for c in CRITERIA if c in EXPECTED[pid]]
        got = calculate_all_strict(players[pid], players, crit, 4,
                                   ruleset="fide-2024")
        for c, want in EXPECTED[pid].items():
            assert got[c] == pytest.approx(want), f"P{pid} {c}"


class TestRatingEdges:
    def test_no_rated_games_zero(self):
        p = PlayerTiebreakData(1, 1500, 0.0, [])
        for crit in CRITERIA:
            got = calculate_all_strict(p, {1: p}, [crit], 4,
                                       ruleset="fide-2024")
            assert got[crit] == 0.0

    def test_zero_score_ptp_rule(self):
        # Zero target -> 800 below the lowest rated opponent (§10.3).
        p = PlayerTiebreakData(1, 1500, 0.0, [g(2, 0.0, rnd=1, rating=1800),
                                              g(3, 0.0, rnd=2, rating=1700)])
        opps = {1: p, 2: PlayerTiebreakData(2, 1800, 1.0, []),
                3: PlayerTiebreakData(3, 1700, 1.0, [])}
        got = calculate_all_strict(p, opps, ["ptp"], 2, ruleset="fide-2024")
        assert got["ptp"] == pytest.approx(900.0)

    def test_unrated_opponents_excluded(self):
        p = PlayerTiebreakData(1, 1500, 1.0, [g(2, 1.0, rnd=1, rating=0),
                                              g(3, 0.0, rnd=2, rating=1800)])
        opps = {1: p, 2: PlayerTiebreakData(2, 0, 0.0, []),
                3: PlayerTiebreakData(3, 1800, 1.0, [])}
        got = calculate_all_strict(p, opps, ["tpr", "aro"], 2,
                                   ruleset="fide-2024")
        # Only the rated game counts: ARO 1800, p 0/1 -> dp -800.
        assert got["aro"] == pytest.approx(1800.0)
        assert got["tpr"] == pytest.approx(1000.0)

    def test_aro_half_up_exact(self):
        # §10.1: 0.5 rounds UP (not banker's). Mean exactly 1812.5.
        # Same rule feeds APRO/APPO (§§10.4–10.5); covered under both
        # FIDE rulesets (identical text).
        p = PlayerTiebreakData(1, 1500, 2.0, [g(2, 1.0, rnd=1, rating=1550),
                                              g(3, 0.0, rnd=2, rating=2100),
                                              g(4, 0.5, rnd=3, rating=1750),
                                              g(5, 0.5, rnd=4, rating=1850)])
        opps = {1: p,
                2: PlayerTiebreakData(2, 1550, 0.0, []),
                3: PlayerTiebreakData(3, 2100, 1.0, []),
                4: PlayerTiebreakData(4, 1750, 0.0, []),
                5: PlayerTiebreakData(5, 1850, 0.0, [])}
        for ruleset in ("fide-2024", "fide-2026"):
            got = calculate_all_strict(p, opps, ["aro"], 4,
                                       ruleset=ruleset)
            assert got["aro"] == 1813.0, ruleset
