"""Direct Encounter §§6.1–6.3 (fide-2024, group-level, Swiss scope).

Basis: FIDE Council document 2024_FC2_18 §6 (PRIMARY, retrieved in full).
Covers: all-met ordering (§6.2), subset reapplication, Swiss certainty
ranking (§6.3 positive + negative), forfeit exclusion (§6.1.1),
repeated-meeting averaging (§6.1.2), fall-through to later criteria,
position sensitivity, and scalar-DE rejection.

All fixtures are points-coherent (points == sum of recorded scores), as
required by fide-2024 strict validation.
"""
import pytest

from tiebreak_core import (
    calculate_all_strict,
    rank_standings_strict,
    UnsupportedCriterionError,
)
from tiebreak_core.models import GameRecord, PlayerTiebreakData


def g(opp, score, color="white", rnd=1, rating=1500, kind="played"):
    return GameRecord(opponent_id=opp, opponent_rating=rating, score=score,
                      color=color, round_number=rnd, kind=kind)


def order(players, criteria, total=3, keys=None):
    res = rank_standings_strict(
        players, criteria, total,
        deterministic_keys=keys or {p: p for p in players},
        ruleset="fide-2024")
    assert res.rules_version == "fide-2024"
    return [p.player_id for p in res.players]


def test_head_to_head_two_players():
    a = PlayerTiebreakData(1, 1500, 2.0, [g(2, 1.0, "white", 1),
                                          g(3, 1.0, "white", 2)])
    b = PlayerTiebreakData(2, 1500, 2.0, [g(1, 0.0, "black", 1),
                                          g(4, 1.0, "white", 2),
                                          g(5, 1.0, "white", 3)])
    c = PlayerTiebreakData(3, 1500, 0.0, [g(1, 0.0, "black", 2)])
    d = PlayerTiebreakData(4, 1500, 0.0, [g(2, 0.0, "black", 2)])
    e = PlayerTiebreakData(5, 1500, 0.0, [g(2, 0.0, "black", 3)])
    players = {1: a, 2: b, 3: c, 4: d, 5: e}
    assert order(players, ["direct_encounter"]) == [1, 2, 3, 4, 5]


def test_cycle_falls_through_to_next_criterion():
    # A>B, B>C, C>A, all tied 1.0: mini 1.0 each, reapply still tied.
    a = PlayerTiebreakData(1, 1500, 1.0, [g(2, 1.0, rnd=1), g(3, 0.0, rnd=2)])
    b = PlayerTiebreakData(2, 1500, 1.0, [g(1, 0.0, rnd=1), g(3, 1.0, rnd=2)])
    c = PlayerTiebreakData(3, 1500, 1.0, [g(1, 1.0, rnd=2), g(2, 0.0, rnd=2)])
    # BH all 2.0 -> deterministic keys decide.
    assert order({1: a, 2: b, 3: c},
                 ["direct_encounter", "buchholz"]) == [1, 2, 3]


def test_subset_reapplication():
    # A,B,C,D tied 2.0. Mini: A/B 2.0, C/D 1.0; subsets split by result.
    a = PlayerTiebreakData(1, 1500, 2.0, [g(2, 1.0, "white", 1),
                                          g(3, 0.5, "white", 2),
                                          g(4, 0.5, "white", 3)])
    b = PlayerTiebreakData(2, 1500, 2.0, [g(1, 0.0, "black", 1),
                                          g(4, 1.0, "white", 2),
                                          g(3, 1.0, "white", 3)])
    c = PlayerTiebreakData(3, 1500, 2.0, [g(5, 1.0, "white", 1),
                                          g(1, 0.5, "black", 2),
                                          g(2, 0.0, "black", 3),
                                          g(4, 0.5, "white", 4)])
    d = PlayerTiebreakData(4, 1500, 2.0, [g(2, 0.0, "black", 2),
                                          g(1, 0.5, "black", 3),
                                          g(3, 0.5, "black", 4),
                                          g(5, 1.0, "white", 5)])
    e = PlayerTiebreakData(5, 1500, 0.0, [g(3, 0.0, "black", 1),
                                          g(4, 0.0, "black", 5)])
    players = {1: a, 2: b, 3: c, 4: d, 5: e}
    # Tiers {A,B} then {C,D} (all BH 6.0 inside) -> key order within.
    assert order(players, ["direct_encounter", "buchholz"],
                 total=5) == [1, 2, 3, 4, 5]


def test_swiss_certainty_ranks_first_alone():
    # A beats B and C; B-C unplayed. A alone-top whatever happens.
    a = PlayerTiebreakData(1, 1500, 2.0, [g(2, 1.0, "white", 1),
                                          g(3, 1.0, "black", 2)])
    b = PlayerTiebreakData(2, 1500, 2.0, [g(1, 0.0, "black", 1),
                                          g(4, 1.0, "white", 2),
                                          g(-1, 1.0, "white", 3, 0,
                                            "pairing_bye")])
    c = PlayerTiebreakData(3, 1500, 2.0, [g(5, 1.0, "white", 1),
                                          g(1, 0.0, "white", 2),
                                          g(-1, 1.0, "white", 3, 0,
                                            "pairing_bye")])
    d = PlayerTiebreakData(4, 1500, 0.0, [g(2, 0.0, "black", 2)])
    e = PlayerTiebreakData(5, 1500, 0.0, [g(3, 0.0, "black", 1)])
    got = order({1: a, 2: b, 3: c, 4: d, 5: e},
                 ["direct_encounter", "buchholz"])
    assert got[0] == 1
    # B and C never met and neither is certain -> BH decides.
    # BH(B): A 2.0 + D 0.0 + dummy 2.0 = 4.0; BH(C): E 0.0 + A 2.0 + 2.0 = 4.0.
    assert got[1:3] == [2, 3]


def test_swiss_no_certainty_falls_through():
    # A>B, B>C, A-C unplayed: A not alone-top in all completions.
    a = PlayerTiebreakData(1, 1500, 2.0, [g(2, 1.0, "white", 1),
                                          g(4, 1.0, "white", 2)])
    b = PlayerTiebreakData(2, 1500, 2.0, [g(1, 0.0, "black", 1),
                                          g(4, 1.0, "white", 2),
                                          g(-1, 1.0, "white", 3, 0,
                                            "pairing_bye")])
    c = PlayerTiebreakData(3, 1500, 2.0, [g(4, 1.0, "white", 1),
                                          g(2, 0.0, "black", 2),
                                          g(-1, 1.0, "white", 3, 0,
                                            "pairing_bye")])
    d = PlayerTiebreakData(4, 1500, 0.0, [g(3, 0.0, "black", 1),
                                          g(1, 0.0, "black", 2)])
    # DE unbroken -> BH: B 6.0 (A 2 + C 2 + dummy 2), C 4.0, A 2.0.
    assert order({1: a, 2: b, 3: c, 4: d},
                 ["direct_encounter", "buchholz"]) == [2, 3, 1, 4]


def test_forfeit_excluded():
    # A "beat" B only by forfeit: excluded from the mini-table (§6.1.1).
    a = PlayerTiebreakData(1, 1500, 2.0, [
        g(2, 1.0, "white", 1, 1500, "forfeit_win"), g(3, 1.0, "white", 2)])
    b = PlayerTiebreakData(2, 1500, 2.0, [
        g(1, 0.0, "black", 1, 1500, "forfeit_loss"), g(4, 1.0, "white", 2),
        g(3, 1.0, "white", 3)])
    c = PlayerTiebreakData(3, 1500, 0.0, [g(1, 0.0, "black", 2),
                                          g(2, 0.0, "black", 3)])
    d = PlayerTiebreakData(4, 1500, 0.0, [g(2, 0.0, "black", 2)])
    # Mini-table empty for A/B (records exist -> all-met path, tied 0-0).
    # BH: A: adj(B)=2.0 + adj(C)=0.0 = 2.0;
    #     B: adj(A)=2.0 + adj(D)=0.0 + adj(C)=0.0 = 2.0 -> keys {1:2, 2:1}.
    assert order({1: a, 2: b, 3: c, 4: d},
                 ["direct_encounter", "buchholz"],
                 keys={1: 2, 2: 1, 3: 3, 4: 4}) == [2, 1, 3, 4]


def test_repeated_meetings_averaged():
    # A vs B twice (win + draw): A averages 0.75, B 0.25 (§6.1.2).
    a = PlayerTiebreakData(1, 1500, 1.5, [g(2, 1.0, rnd=1), g(2, 0.5, rnd=2)])
    b = PlayerTiebreakData(2, 1500, 1.5, [g(1, 0.0, rnd=1), g(1, 0.5, rnd=2),
                                          g(3, 1.0, rnd=3)])
    c = PlayerTiebreakData(3, 1500, 0.0, [g(2, 0.0, rnd=3)])
    assert order({1: a, 2: b, 3: c}, ["direct_encounter"]) == [1, 2, 3]


def test_scalar_direct_encounter_rejected():
    a = PlayerTiebreakData(1, 1500, 1.0, [g(2, 1.0, rnd=1)])
    b = PlayerTiebreakData(2, 1500, 0.0, [g(1, 0.0, rnd=1)])
    with pytest.raises(UnsupportedCriterionError):
        calculate_all_strict(a, {1: a, 2: b}, ["direct_encounter"], 2,
                             ruleset="fide-2024")


def test_values_carry_scalars_only():
    a = PlayerTiebreakData(1, 1500, 2.0, [g(2, 1.0, rnd=1),
                                          g(-1, 1.0, rnd=2, kind="pairing_bye")])
    b = PlayerTiebreakData(2, 1500, 0.0, [g(1, 0.0, rnd=1)])
    res = rank_standings_strict({1: a, 2: b},
                                ["direct_encounter", "buchholz"], 2,
                                ruleset="fide-2024")
    assert "direct_encounter" not in res.players[0].values
    assert res.players[0].values["buchholz"] == pytest.approx(2.0)


def test_position_sensitivity():
    # BH first: A/B tied BH; DE inside the BH tie puts A first.
    a = PlayerTiebreakData(1, 1500, 2.0, [g(2, 1.0, "white", 1),
                                          g(-1, 1.0, "white", 2, 0,
                                            "pairing_bye")])
    b = PlayerTiebreakData(2, 1500, 2.0, [g(1, 0.0, "black", 1),
                                          g(4, 1.0, "white", 2),
                                          g(-1, 1.0, "white", 3, 0,
                                            "pairing_bye")])
    c = PlayerTiebreakData(3, 1500, 0.5, [g(5, 0.5, "white", 1)])
    d = PlayerTiebreakData(4, 1500, 0.0, [g(2, 0.0, "black", 2)])
    e = PlayerTiebreakData(5, 1500, 0.5, [g(3, 0.5, "black", 1)])
    # BH: A: adj(B)=2.0 + dummy 2.0 = 4.0;
    #     B: adj(A)=2.0 + adj(D)=0.0 + dummy 2.0 = 4.0 -> DE: A won.
    assert order({1: a, 2: b, 3: c, 4: d, 5: e},
                 ["buchholz", "direct_encounter"]) == [1, 2, 3, 5, 4]


def test_incoherent_points_rejected():
    a = PlayerTiebreakData(1, 1500, 2.0, [g(2, 1.0, rnd=1)])
    b = PlayerTiebreakData(2, 1500, 0.0, [g(1, 0.0, rnd=1)])
    from tiebreak_core import InvalidPlayerDataError
    with pytest.raises(InvalidPlayerDataError):
        calculate_all_strict(a, {1: a, 2: b}, ["buchholz"], 2,
                             ruleset="fide-2024")
