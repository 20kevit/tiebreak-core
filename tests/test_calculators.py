"""Tiebreak calculators — ported verbatim from chess-manager tests/domain/test_tiebreak.py.

Imports changed from ``domain.tiebreak.*`` to ``tiebreak_core.*``.
Expectations unchanged (behavior-preserving extraction).
"""
import pytest
from tiebreak_core.calculators import (
    buchholz, buchholz_cut1, buchholz_cut2, median_buchholz,
    sonneborn_berger, progressive, wins_count, wins_with_black,
    games_with_black, average_rating_opponents, koya, direct_encounter,
    buchholz_sum, arpo, calculate_all, TIEBREAK_REGISTRY,
)
from tiebreak_core.registry import TIEBREAK_IDS
from tiebreak_core.models import PlayerTiebreakData, GameRecord

def rec(opp, score, color='white', rnd=1, opp_rating=1500):
    return GameRecord(opponent_id=opp, opponent_rating=opp_rating, score=score, color=color, round_number=rnd)

def pdata(pid, rating, points, games, wins_bb=None):
    return PlayerTiebreakData(player_id=pid, rating=rating, points=points, games=games)

# Helper to create 4-player round robin after 3 rounds
def four_player_fixture():
    p1 = pdata(1, 2000, 2.5, [rec(2,1,rnd=1), rec(3,0.5,rnd=2), rec(4,1,rnd=3)])
    p2 = pdata(2, 1900, 1.0, [rec(1,0,rnd=1), rec(3,0.5,rnd=2), rec(4,0.5,rnd=3)])
    p3 = pdata(3, 1800, 1.5, [rec(1,0.5,rnd=1), rec(2,0.5,rnd=2), rec(4,0.5,rnd=3)])
    p4 = pdata(4, 1700, 1.0, [rec(1,0,rnd=1), rec(2,0.5,rnd=2), rec(3,0.5,rnd=3)])
    allp = {1:p1,2:p2,3:p3,4:p4}
    return p1,p2,p3,p4,allp

class TestBuchholzFamily:
    def test_buchholz_basic(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        assert buchholz(p1, allp) == pytest.approx(3.5)
        assert buchholz(p2, allp) == pytest.approx(5.0)

    def test_buchholz_cut1(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        assert buchholz_cut1(p1, allp) == pytest.approx(2.5)
        p = pdata(10,1500,1.0,[rec(2,1)])
        ap = {2: pdata(2,1600,1.0,[]), 10:p}
        assert buchholz_cut1(p, ap) == pytest.approx(1.0)

    def test_buchholz_cut2(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        assert buchholz_cut2(p2, allp) == pytest.approx(2.5)
        p = pdata(10,1500,1.0,[rec(2,1), rec(3,0.5)])
        ap = {2:pdata(2,1600,0.5,[]),3:pdata(3,1600,1.0,[]),10:p}
        assert buchholz_cut2(p, ap) == pytest.approx(1.0)

    def test_median_buchholz(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        assert median_buchholz(p1, allp) == pytest.approx(1.0)
        p = pdata(10,1500,1.0,[rec(2,1)])
        ap = {2:pdata(2,1600,2.0,[]),10:p}
        assert median_buchholz(p, ap) == buchholz(p, ap)

    def test_buchholz_zero_games(self):
        p = pdata(1,1500,0.0,[])
        assert buchholz(p, {}) == 0.0
        assert buchholz_cut1(p, {}) == 0.0
        assert buchholz_cut2(p, {}) == 0.0
        assert median_buchholz(p, {}) == 0.0

    def test_buchholz_virtual_opponent(self):
        p = pdata(1,1500,2.0,[rec(-1,1,rnd=1), rec(2,1,rnd=2)])
        allp = {2:pdata(2,1600,1.0,[]),1:p}
        assert buchholz(p, allp) == pytest.approx(2.0)

    def test_buchholz_sum(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        b2 = buchholz(p2, allp)
        b3 = buchholz(p3, allp)
        b4 = buchholz(p4, allp)
        assert buchholz_sum(p1, allp) == pytest.approx(round(b2+b3+b4,1))

class TestSonnebornBerger:
    def test_sonneborn_basic(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        assert sonneborn_berger(p1, allp) == pytest.approx(2.75)
        assert sonneborn_berger(p3, allp) == pytest.approx(2.25)

    def test_sonneborn_virtual_opponent(self):
        p = pdata(1,1500,1.5,[rec(-1,1,rnd=1), rec(2,0.5,rnd=2)])
        allp = {2:pdata(2,1600,1.0,[]),1:p}
        assert sonneborn_berger(p, allp) == pytest.approx(1.0)

    def test_sonneborn_zero(self):
        p = pdata(1,1500,0.0,[])
        assert sonneborn_berger(p,{}) == 0.0

class TestProgressive:
    def test_progressive_cumulative(self):
        p = pdata(1,1500,2.0,[rec(2,1,rnd=1), rec(3,0.5,rnd=2), rec(4,0.5,rnd=3)])
        assert progressive(p,{}) == pytest.approx(4.5)

    def test_progressive_unsorted(self):
        p = pdata(1,1500,2.0,[rec(4,0.5,rnd=3), rec(2,1,rnd=1), rec(3,0.5,rnd=2)])
        assert progressive(p,{}) == pytest.approx(4.5)

    def test_progressive_zero(self):
        p = pdata(1,1500,0.0,[])
        assert progressive(p,{}) == 0.0

class TestWinsAndBlack:
    def test_wins_count(self):
        p = pdata(1,1500,2.0,[rec(2,1), rec(3,1), rec(4,0.5)])
        assert wins_count(p,{}) == 2.0
        p0 = pdata(2,1500,0.0,[rec(1,0),rec(3,0)])
        assert wins_count(p0,{}) == 0.0

    def test_wins_with_black(self):
        p = pdata(1,1500,2.0,[rec(2,1,color='black'), rec(3,1,color='white'), rec(4,0.5,color='black')])
        assert wins_with_black(p,{}) == 1.0

    def test_games_with_black(self):
        p = pdata(1,1500,1.0,[rec(2,1,color='black'), rec(3,0,color='black'), rec(4,0.5,color='white')])
        assert games_with_black(p,{}) == 2.0

class TestAROKoyaArpo:
    def test_aro_average(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        assert average_rating_opponents(p1, allp) == 1800

    def test_aro_ignores_zero_rating(self):
        p = pdata(1,1500,1.0,[rec(2,1,opp_rating=0), rec(3,1,opp_rating=1600)])
        allp = {2:pdata(2,0,0,[]),3:pdata(3,1600,0,[]),1:p}
        assert average_rating_opponents(p, allp) == 1600

    def test_aro_virtual(self):
        p = pdata(1,1800,1.0,[rec(-1,1,opp_rating=0)])
        assert average_rating_opponents(p,{1:p}) == 1800

    def test_aro_no_games(self):
        p = pdata(1,1500,0.0,[])
        assert average_rating_opponents(p,{}) == 0.0

    def test_koya_half_score(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        assert koya(p1, allp, total_rounds=3) == pytest.approx(0.5)
        assert koya(p1, allp, total_rounds=0) == 0.0

    def test_arpo_basic(self):
        opp = pdata(2,1600,1.0,[rec(3,0.5,opp_rating=1500), rec(4,0.5,opp_rating=1700)])
        p = pdata(1,1500,1.0,[rec(2,1)])
        allp = {1:p,2:opp,3:pdata(3,1500,0.5,[]),4:pdata(4,1700,0.5,[])}
        assert arpo(p, allp) == 1600

    def test_arpo_no_data(self):
        p = pdata(1,1500,0.0,[rec(99,1)])
        assert arpo(p,{}) == 0.0

class TestDirectEncounter:
    def test_direct_encounter_hit(self):
        p = pdata(1,1500,1.0,[rec(2,1), rec(3,0.5)])
        allp = {2:pdata(2,1500,0,[])}
        assert direct_encounter(p, allp, opponent_id=2) == 1.0
        assert direct_encounter(p, allp, opponent_id=3) == 0.5
        assert direct_encounter(p, allp, opponent_id=99) == 0.0

class TestRegistry:
    def test_all_tiebreaks_registered(self):
        expected_names = set(TIEBREAK_IDS)
        for name in expected_names:
            if name in ("koya","direct_encounter"):
                continue
            assert name in TIEBREAK_REGISTRY, f"{name} missing"

    def test_calculate_all_dispatch(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        res = calculate_all(p1, allp, ["buchholz","sonneborn_berger","wins","koya","direct_encounter","nonexistent"], total_rounds=3)
        assert "buchholz" in res
        assert "sonneborn_berger" in res
        assert "wins" in res
        assert res["koya"] == koya(p1, allp, total_rounds=3)
        assert res["direct_encounter"] == 0.0
        assert res["nonexistent"] == 0.0

    def test_deterministic(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        r1 = calculate_all(p1, allp, ["buchholz","progressive","aro"], total_rounds=3)
        r2 = calculate_all(p1, allp, ["buchholz","progressive","aro"], total_rounds=3)
        assert r1 == r2
