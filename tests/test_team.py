"""Team domain (C.07 §§11–13): definition-derived conformance."""
import copy

import pytest

from tiebreak_core.errors import (
    InvalidDescriptorError,
    InvalidPlayerDataError,
    UnsupportedCriterionError,
)
from tiebreak_core.team import (
    TeamFormat,
    TeamMatch,
    TeamRecord,
    bbe_key,
    board_count,
    calculate_team,
    rank_team_standings,
    sssc,
    tbr_key,
    validate_teams,
)

FMT = TeamFormat(mp_win=2.0, mp_draw=1.0)


@pytest.fixture()
def league4():
    """Four-team round robin; all matches contested.

    Hand-derived expectations (see test bodies):
    MP: T1=5, T2=3, T3=2, T4=1. GP: T1=9.5, T2=7, T3=6, T4=4.5.
    """
    return {
        1: TeamRecord(1, 5.0, 9.5, [
            TeamMatch(2, 1, 2, 3.0), TeamMatch(3, 2, 2, 3.5),
            TeamMatch(4, 3, 1, 3.0)], (3.5, 2.5, 2.0, 1.5)),
        2: TeamRecord(2, 3.0, 7.0, [
            TeamMatch(1, 1, 0, 1.0), TeamMatch(4, 2, 2, 3.0),
            TeamMatch(3, 3, 1, 3.0)], (2.5, 2.0, 1.5, 1.0)),
        3: TeamRecord(3, 2.0, 6.0, [
            TeamMatch(4, 1, 1, 2.0), TeamMatch(1, 2, 0, 0.5),
            TeamMatch(2, 3, 1, 3.5)], (2.0, 1.5, 1.5, 1.0)),
        4: TeamRecord(4, 1.0, 4.5, [
            TeamMatch(3, 1, 1, 2.0), TeamMatch(2, 2, 0, 1.0),
            TeamMatch(1, 3, 0, 1.5)], (1.5, 1.0, 1.0, 1.5)),
    }


TR = 3


# ------------------------------------------------------------------
# Article 13.2 — ESB four combos (§13.2.1–13.2.4)
# ------------------------------------------------------------------

def test_esb_four_combos(league4):
    # T1 EMMSB = 2*3.0 + 2*2.0 + 1*1.0 = 11.0
    assert calculate_team(league4[1], league4, "EMMSB", TR, FMT) == \
        pytest.approx(11.0)
    # T1 EMGSB = 3.0*3.0 + 2.0*3.5 + 1.0*3.0 = 19.0
    assert calculate_team(league4[1], league4, "EMGSB", TR, FMT) == \
        pytest.approx(19.0)
    # T1 EGMSB = 2*7.0 + 2*6.0 + 1*4.5 = 30.5
    assert calculate_team(league4[1], league4, "EGMSB", TR, FMT) == \
        pytest.approx(30.5)
    # T1 EGGSB = 3.0*7.0 + 3.5*6.0 + 3.0*4.5 = 55.5
    assert calculate_team(league4[1], league4, "EGGSB", TR, FMT) == \
        pytest.approx(55.5)
    # T4 EGGSB = 2.0*6.0 + 1.0*7.0 + 0.5*... : 2*6+1*7+1.5*9.5 = 33.25
    assert calculate_team(league4[4], league4, "EGGSB", TR, FMT) == \
        pytest.approx(33.25)


def test_esb_cut_lowest_basis(league4):
    # T1 EMMSB/C1: bases (opp MP) 3.0/2.0/1.0 -> cut T4 leg (1.0).
    assert calculate_team(league4[1], league4, "EMMSB/C1", TR, FMT) == \
        pytest.approx(10.0)
    # T1 EGMSB/C1: bases (opp GP) 7.0/6.0/4.5 -> cut T4 leg (4.5).
    assert calculate_team(league4[1], league4, "EGMSB/C1", TR, FMT) == \
        pytest.approx(26.0)


def test_esb_cut_lowest_basis_tie_break():
    # Two opponents share the lowest MP basis (1.0): cut the lowest
    # contribution among them (§14.1.2 "if there is more than one
    # such opponent, exclude the lowest contribution").
    teams = {
        1: TeamRecord(1, 4.0, 8.0, [
            TeamMatch(2, 1, 2, 3.0), TeamMatch(3, 2, 2, 2.0),
            TeamMatch(4, 3, 0, 1.0)]),
        2: TeamRecord(2, 1.0, 3.0, [TeamMatch(1, 1, 0, 1.0)]),
        3: TeamRecord(3, 3.0, 5.0, [TeamMatch(1, 2, 0, 2.0)]),
        4: TeamRecord(4, 1.0, 2.0, [TeamMatch(1, 3, 2, 3.0)]),
    }
    # Legs: T2 2*1.0=2.0; T3 2*3.0=6.0; T4 0*1.0=0.0. Lowest basis 1.0
    # shared by T2/T4 -> cut min contribution 0.0 -> 8.0.
    assert calculate_team(teams[1], teams, "EMMSB/C1", 3, FMT) == \
        pytest.approx(8.0)


def test_esb_cut3_rejected(league4):
    # Rejected at parse time (no FIDE ESB-C3 semantics exist).
    with pytest.raises(InvalidDescriptorError):
        calculate_team(league4[1], league4, "EMMSB/C3", TR, FMT)


# ------------------------------------------------------------------
# Article 13.4 — SSSC
# ------------------------------------------------------------------

def test_sssc_default_normaliser(league4):
    # T1: secondary GP 9.5 + BH_MP(3+2+1=6) / trunc(3*2/4)=1 -> 15.5
    assert sssc(league4[1], league4, TR, FMT) == pytest.approx(15.5)
    assert calculate_team(league4[1], league4, "SSSC", TR, FMT) == \
        pytest.approx(15.5)


def test_sssc_custom_k(league4):
    # 9.5 + 6/4 = 11.0
    assert calculate_team(league4[1], league4, "SSSC/K4", TR, FMT) == \
        pytest.approx(11.0)


def test_sssc_gp_primary(league4):
    # Primary GP: secondary MP 5.0 + BH_GP(7+6+4.5=17.5)/trunc(3*4/2)=6
    # -> 5.0 + 17.5/6
    assert calculate_team(league4[1], league4, "SSSC", TR, FMT,
                          primary="GP") == pytest.approx(5.0 + 17.5 / 6)


def test_mpvgp(league4):
    assert calculate_team(league4[1], league4, "MPvGP", TR, FMT) == \
        pytest.approx(9.5)
    assert calculate_team(league4[1], league4, "MPvGP", TR, FMT,
                          primary="GP") == pytest.approx(5.0)


# ------------------------------------------------------------------
# Article 12 — BC / TBR / BBE
# ------------------------------------------------------------------

def test_board_count(league4):
    # T1: 1*3.5+2*2.5+3*2.0+4*1.5 = 20.5
    assert board_count(league4[1], league4, TR, FMT) == pytest.approx(20.5)
    assert calculate_team(league4[1], league4, "BC", TR, FMT) == \
        pytest.approx(20.5)
    assert calculate_team(league4[4], league4, "BC", TR, FMT) == \
        pytest.approx(12.5)


def test_board_count_ascending_in_ranking(league4):
    # Equal MP+GP pair: lower BC must rank first (§12.1).
    # T1 BC = 1*1.0+2*3.0 = 7.0; T2 BC = 1*3.0+2*1.0 = 5.0.
    teams = {
        1: TeamRecord(1, 2.0, 4.0, [TeamMatch(2, 1, 1, 2.0)], (1.0, 3.0)),
        2: TeamRecord(2, 2.0, 4.0, [TeamMatch(1, 1, 1, 2.0)], (3.0, 1.0)),
    }
    ranked = rank_team_standings(teams, ["BC"], 1, FMT)
    assert [t.team_id for t in ranked.teams] == [2, 1]


def test_tbr_bbe_keys(league4):
    assert tbr_key(league4[1]) == (3.5, 2.5, 2.0, 1.5)
    assert bbe_key(league4[1]) == (8.0, 6.0, 3.5, 0.0)
    assert calculate_team(league4[1], league4, "TBR", TR, FMT) == \
        pytest.approx(3.5)
    assert calculate_team(league4[1], league4, "BBE", TR, FMT) == \
        pytest.approx(8.0)


def test_tbr_reapplication_in_ranking():
    teams = {
        1: TeamRecord(1, 2.0, 4.0, [TeamMatch(2, 1, 1, 2.0)],
                      (2.0, 2.0, 0.0)),
        2: TeamRecord(2, 2.0, 4.0, [TeamMatch(1, 1, 1, 2.0)],
                      (2.0, 1.0, 1.0)),
    }
    ranked = rank_team_standings(teams, ["TBR"], 1, FMT)
    assert [t.team_id for t in ranked.teams] == [1, 2]  # board-2 decides


# ------------------------------------------------------------------
# Article 13.3 — EDE
# ------------------------------------------------------------------

def _ede_fixture():
    # A=1 beats B=2 (2-0), draws C=3 (1-1), B beats C (2-0).
    # Mini MP: A=3, B=2, C=1 -> order 1,2,3 at equal primary.
    return {
        1: TeamRecord(1, 3.0, 4.0, [TeamMatch(2, 1, 2, 3.0),
                                    TeamMatch(3, 2, 1, 2.0)]),
        2: TeamRecord(2, 3.0, 4.0, [TeamMatch(1, 1, 0, 1.0),
                                    TeamMatch(3, 2, 2, 3.0)]),
        3: TeamRecord(3, 3.0, 4.0, [TeamMatch(1, 1, 1, 2.0),
                                    TeamMatch(2, 2, 0, 1.0)]),
    }


def test_ede_complete_meeting():
    teams = _ede_fixture()
    ranked = rank_team_standings(teams, ["EDE"], 2, FMT)
    assert [t.team_id for t in ranked.teams] == [1, 2, 3]


def test_ede_secondary_stage():
    # Primary tied in the mini-table (all draws), GP mini decides.
    teams = {
        1: TeamRecord(1, 2.0, 5.0, [TeamMatch(2, 1, 1, 3.0),
                                    TeamMatch(3, 2, 1, 2.0)]),
        2: TeamRecord(2, 2.0, 4.0, [TeamMatch(1, 1, 1, 1.0),
                                    TeamMatch(3, 2, 1, 3.0)]),
        3: TeamRecord(3, 2.0, 3.0, [TeamMatch(1, 1, 1, 2.0),
                                    TeamMatch(2, 2, 1, 1.0)]),
    }
    ranked = rank_team_standings(teams, ["EDE"], 2, FMT)
    assert [t.team_id for t in ranked.teams] == [1, 2, 3]


def test_ede_incomplete_certainty():
    # A beat B; C met nobody. A (2 mini MP) is certain whatever the
    # missing results (ceiling 2/match): A first, B/C fall through.
    teams = {
        1: TeamRecord(1, 2.0, 3.0, [TeamMatch(2, 1, 2, 3.0)]),
        2: TeamRecord(2, 2.0, 3.0, [TeamMatch(1, 1, 0, 1.0)]),
        3: TeamRecord(3, 2.0, 3.0, []),
    }
    ranked = rank_team_standings(teams, ["EDE"], 2, FMT)
    assert ranked.teams[0].team_id == 1
    assert {t.team_id for t in ranked.teams[1:]} == {2, 3}


def test_ede_is_group_stage_not_scalar(league4):
    with pytest.raises(UnsupportedCriterionError):
        calculate_team(league4[1], league4, "EDE", TR, FMT)


def test_chain_pair_only(league4):
    # EDEBT on a 3+ way group degrades to EDE (chains are pair-only).
    ranked = rank_team_standings(league4, ["EDEBT"], TR, FMT)
    assert [t.team_id for t in ranked.teams][:1] == [1]


def test_chain_breaks_pair_via_bc():
    # Pair tied on MP+GP and split EDE (no meeting): BC decides.
    teams = {
        1: TeamRecord(1, 2.0, 4.0, [TeamMatch(2, 1, 0, 1.0)], (1.0, 3.0)),
        2: TeamRecord(2, 2.0, 4.0, [TeamMatch(1, 1, 2, 3.0)], (3.0, 1.0)),
    }
    ranked = rank_team_standings(teams, ["EDEBT"], 1, FMT)
    # EDE: 2 beat 1 -> [2, 1] already; chain not needed but must hold.
    assert [t.team_id for t in ranked.teams] == [2, 1]


# ------------------------------------------------------------------
# Table-2 reuse on MP/GP reference (§13 blanket rule)
# ------------------------------------------------------------------

def test_table2_reference_scores(league4):
    assert calculate_team(league4[1], league4, "WIN:MP", TR, FMT) == \
        pytest.approx(2.0)
    assert calculate_team(league4[3], league4, "WIN:MP", TR, FMT) == \
        pytest.approx(0.0)
    assert calculate_team(league4[1], league4, "WON:MP", TR, FMT) == \
        pytest.approx(2.0)
    # PS:GP T1: cumulative 3.0, 6.5, 9.5 -> 19.0
    assert calculate_team(league4[1], league4, "PS:GP", TR, FMT) == \
        pytest.approx(19.0)
    # PS:MP/C1 T1: MP cumulative 2,4,5 -> 11-2 = 9
    assert calculate_team(league4[1], league4, "PS:MP/C1", TR, FMT) == \
        pytest.approx(9.0)
    # BH:MP T1 = 3+2+1 = 6
    assert calculate_team(league4[1], league4, "BH:MP", TR, FMT) == \
        pytest.approx(6.0)
    # KS:GP T1: threshold 3*4/2=6: T2(7.0)+T3(6.0) qualify -> 3.0+3.5
    assert calculate_team(league4[1], league4, "KS:GP", TR, FMT) == \
        pytest.approx(6.5)
    # KS:GP/L+1 T1: threshold 6.5 -> T2 only -> 3.0
    assert calculate_team(league4[1], league4, "KS:GP/L+1", TR, FMT) == \
        pytest.approx(3.0)


def test_aob_fb_team(league4):
    assert calculate_team(league4[1], league4, "AOB:MP", TR, FMT) == \
        pytest.approx((8.0 + 9.0 + 10.0) / 3)
    # FB:GP T1: final round (R3) drawn: T2 7+(2-3)=6, T3 6+(2-3.5)=4.5,
    # T4 4.5+(2-1.5)=5 -> 15.5
    assert calculate_team(league4[1], league4, "FB:GP", TR, FMT) == \
        pytest.approx(15.5)


# ------------------------------------------------------------------
# Invalid inputs
# ------------------------------------------------------------------

def test_team_validation():
    with pytest.raises(InvalidPlayerDataError):
        validate_teams({1: TeamRecord(2, 1.0, 1.0, [])})  # key mismatch
    with pytest.raises(InvalidPlayerDataError):
        validate_teams("nope")
    bad = TeamRecord(1, 1.0, 1.0, [TeamMatch(2, 1, -1, 1.0)])
    with pytest.raises(InvalidPlayerDataError):
        validate_teams({1: bad})
    bad_kind = TeamRecord(1, 1.0, 1.0, [
        TeamMatch(2, 1, 1, 1.0, kind="whatever")])
    with pytest.raises(InvalidPlayerDataError):
        validate_teams({1: bad_kind})


def test_board_codes_need_boards(league4):
    boardless = dict(league4)
    boardless[1] = TeamRecord(1, 5.0, 9.5, league4[1].matches, ())
    with pytest.raises(InvalidPlayerDataError):
        calculate_team(boardless[1], boardless, "BC", TR, FMT)


def test_individual_descriptor_rejected(league4):
    with pytest.raises(UnsupportedCriterionError):
        calculate_team(league4[1], league4, "BH/C1", TR, FMT)
    with pytest.raises(InvalidDescriptorError):
        calculate_team(league4[1], league4, "SB/M1", TR, FMT)


def test_team_non_mutation(league4):
    before = copy.deepcopy(league4)
    for tid in league4:
        for descriptor in ("EMMSB", "EMGSB/C1", "SSSC", "SSSC/K4",
                           "BH:MP/C1", "KS:GP/L+1", "EDEBT"):
            try:
                calculate_team(league4[tid], league4, descriptor, TR,
                               FMT)
            except UnsupportedCriterionError:
                pass
    rank_team_standings(league4, ["EMMSB", "EDE", "BC"], TR, FMT)
    assert league4 == before


def test_team_determinism(league4):
    first = rank_team_standings(league4, ["EMMSB", "EDE", "BC"], TR, FMT)
    second = rank_team_standings(league4, ["EMMSB", "EDE", "BC"], TR, FMT)
    assert first == second
