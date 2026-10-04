"""Independent differential validation (echecs oracle).

Compares tiebreak-core against COMMITTED third-party values
(`tests/oracle/echecs_4.1.json`, generated from MIT-licensed
@echecs/* packages — see `tests/oracle/README.md`; no node/network
at test time). The oracle is independent code implementing the same
FIDE text, so agreement guards implementation bugs (not shared
spec misreadings — those are covered by official corpus).

Comparison contract (see oracle README for rationale):
- EXACT (|diff| <= 1e-9): BH/C1/C2/M1/M2, FB/C1/C2, SB/C1/C2, ARO
  (+C1/C2), PS, Koya on fully-played fixtures, under fide-2026
  Swiss; plus fide-2024 on fully-played fixtures (caps inert).
- AOB/AOB-FB: |diff| <= 0.51 (oracle rounds to integer; core exact).
- progressive_cut1: SKIPPED — oracle contradicts FIDE §14.1.1.c
  (official TEC 16/16 PS-C1 table matches tiebreak-core).
- fore_median1/2, aro_median1/2: core must raise
  UnknownCriterionError (generic machine deferred, explicit).
- Koya: fully-played fixtures only (threshold-basis divergence on
  bye-inflated scores documented in oracle README).
- DE: order comparison on all-met groups only (scalar mini-score
  ordering coincides with §6.2 there); recursion/certainty stay
  article-tested.

Any mismatch: minimize, determine the correct side from FIDE text,
never auto-edit the implementation to match the oracle.
"""
import json
import pathlib

import pytest

from tiebreak_core import calculate_strict, rank_standings_strict
from tiebreak_core.errors import UnknownCriterionError
from tiebreak_core.models import GameRecord, PlayerTiebreakData

ORACLE_PATH = pathlib.Path(__file__).parent / "oracle" / "echecs_4.1.json"

EXACT = ["buchholz", "buchholz_cut1", "buchholz_cut2",
         "median_buchholz", "median_buchholz_2", "fore_buchholz",
         "fore_buchholz_cut1", "fore_buchholz_cut2",
         "sonneborn_berger", "sonneborn_berger_cut1",
         "sonneborn_berger_cut2", "aro", "aro_cut1", "aro_cut2",
         "progressive"]
FP_ONLY = {"koya"}
AVERAGES = ["aob", "aob_fb"]
UNSUPPORTED = ["fore_median1", "fore_median2",
               "aro_median1", "aro_median2"]


def _load():
    doc = json.loads(ORACLE_PATH.read_text())
    return doc["meta"], doc["cases"]


META, CASES = _load()


def _build(spec):
    players = {}
    for pid, p in spec.items():
        players[int(pid)] = PlayerTiebreakData(
            player_id=int(pid), rating=p["rating"], points=p["points"],
            games=[GameRecord(opponent_id=g["opponent"],
                              opponent_rating=g.get("rating", 0),
                              score=g["score"], color=g["color"],
                              round_number=g["round"],
                              kind=g.get("kind", ""))
                   for g in p["games"]])
    return players


def _oracle_value(case, pid, crit):
    value = case["echecks"][str(pid)][crit]
    assert not isinstance(value, str), (
        f"oracle has no number for {crit} (got {value!r})")
    return value


def _case_ids():
    return sorted(CASES)


# de_trio is a Direct-Encounter ordering fixture (short records for
# context players would hit documented cut/median edge policies, not
# shared defined behavior) — scalar differential excludes it.
SCALAR_CASES = [n for n in _case_ids() if n != "de_trio"]


def _is_fully_played(case):
    for p in case["fixture"]["players"].values():
        for g in p["games"]:
            if (g.get("kind", "") or "played") != "played":
                return False
    return True


def _has_repeats(case):
    seen = set()
    for pid, p in case["fixture"]["players"].items():
        for g in p["games"]:
            if (g.get("kind", "") or "played") != "played":
                continue
            pair = (min(int(pid), g["opponent"]), max(int(pid), g["opponent"]))
            if pair in seen:
                return True
            seen.add(pair)
    return False


@pytest.mark.parametrize("name", SCALAR_CASES)
@pytest.mark.parametrize("criterion", EXACT)
def test_exact_agreement_fide2026(name, criterion):
    case = CASES[name]
    players = _build(case["fixture"]["players"])
    total = case["fixture"]["total_rounds"]
    for pid, pdata in players.items():
        want = _oracle_value(case, pid, criterion)
        got = calculate_strict(pdata, players, criterion, total,
                               ruleset="fide-2026")
        assert got == pytest.approx(want, abs=1e-9), (
            f"{name} player {pid} {criterion}: core {got} vs "
            f"echecs {want}")


@pytest.mark.parametrize("name", SCALAR_CASES)
def test_koya_fully_played_only(name):
    case = CASES[name]
    if not _is_fully_played(case):
        pytest.skip("Koya threshold basis diverges on bye-inflated "
                    "scores (documented); fully-played events only")
    if _has_repeats(case):
        pytest.skip("echecs Koya double-counts repeated meetings "
                    "(RR-only scope); true round-robins only")
    players = _build(case["fixture"]["players"])
    total = case["fixture"]["total_rounds"]
    for pid, pdata in players.items():
        want = _oracle_value(case, pid, "koya")
        got = calculate_strict(pdata, players, "koya", total,
                               ruleset="fide-2026")
        assert got == pytest.approx(want, abs=1e-9), (
            f"{name} player {pid} koya: core {got} vs echecs {want}")


@pytest.mark.parametrize("name", SCALAR_CASES)
@pytest.mark.parametrize("criterion", AVERAGES)
def test_average_with_integer_rounding_tolerance(name, criterion):
    case = CASES[name]
    players = _build(case["fixture"]["players"])
    total = case["fixture"]["total_rounds"]
    for pid, pdata in players.items():
        want = _oracle_value(case, pid, criterion)
        got = calculate_strict(pdata, players, criterion, total,
                               ruleset="fide-2026")
        # Oracle rounds means to integer; core keeps exact means.
        assert abs(got - want) <= 0.51, (
            f"{name} player {pid} {criterion}: core {got} vs "
            f"echecs {want}")


@pytest.mark.parametrize("name", [n for n in SCALAR_CASES
                                  if _is_fully_played(CASES[n])])
@pytest.mark.parametrize("criterion", EXACT + ["koya"])
def test_edition_coincidence_fide2024(name, criterion):
    # Fully-played events have no unplayed rounds, so caps/dummies are
    # inert: fide-2024 must equal both fide-2026 and the oracle — but
    # only for criteria the 2024 engine implements (C2/FB-combos are
    # fide-2026-only ids).
    from tiebreak_core import fide2024 as _f24
    if criterion not in _f24.FIDE2024_REGISTRY:
        pytest.skip(f"{criterion} is fide-2026-only")
    case = CASES[name]
    if criterion == "koya" and _has_repeats(case):
        pytest.skip("echecs Koya double-counts repeated meetings "
                    "(RR-only scope); true round-robins only")
    players = _build(case["fixture"]["players"])
    total = case["fixture"]["total_rounds"]
    for pid, pdata in players.items():
        want = _oracle_value(case, pid, criterion)
        got = calculate_strict(pdata, players, criterion, total,
                               ruleset="fide-2024")
        assert got == pytest.approx(want, abs=1e-9), (
            f"{name} player {pid} {criterion} (2024): core {got} "
            f"vs echecs {want}")


@pytest.mark.parametrize("limit,oracle_key",
                         [(-1.0, "koya_limit_m2"),
                          (-0.5, "koya_limit_m1"),
                          (0.5, "koya_limit_p1"),
                          (1.0, "koya_limit_p2")])
@pytest.mark.parametrize("ruleset", ["fide-2024", "fide-2026"])
def test_koya_limits_agree_true_rr(limit, oracle_key, ruleset):
    # True round-robin only (echecs Koya double-counts repeated
    # meetings; its documented RR-only scope).
    case = CASES["rr_8x7"]
    players = _build(case["fixture"]["players"])
    total = case["fixture"]["total_rounds"]
    for pid, pdata in players.items():
        want = _oracle_value(case, pid, oracle_key)
        got = calculate_strict(pdata, players, "koya", total,
                               ruleset=ruleset, koya_limit=limit)
        assert got == pytest.approx(want, abs=1e-9), (
            f"rr_8x7 player {pid} koya_limit={limit} ({ruleset}): "
            f"core {got} vs echecs {want}")


@pytest.mark.parametrize("criterion", UNSUPPORTED)
def test_generic_combos_explicitly_unsupported(criterion):
    players = _build(CASES["fp_6x5"]["fixture"]["players"])
    pdata = players[1]
    with pytest.raises(UnknownCriterionError):
        calculate_strict(pdata, players, criterion, 5,
                         ruleset="fide-2026")
    players = _build(CASES["fp_6x5"]["fixture"]["players"])
    pdata = players[1]
    with pytest.raises(UnknownCriterionError):
        calculate_strict(pdata, players, criterion, 5,
                         ruleset="fide-2026")


def test_de_order_all_met_groups():
    # All-met groups: scalar mini-score order coincides with §6.2
    # tier order. Recursion/certainty paths stay article-tested.
    case = CASES["de_trio"]
    players = _build(case["fixture"]["players"])
    total = case["fixture"]["total_rounds"]
    order = [p.player_id for p in
             rank_standings_strict(players, ["direct_encounter"], total,
                                   deterministic_keys={i: i for i in
                                                       players},
                                   ruleset="fide-2026").players]
    mini = {pid: case["echecks"][str(pid)]["de_score"] for pid in players
            if players[pid].points == 2.0}
    assert [p for p in order if p in mini] == sorted(
        mini, key=lambda pid: -mini[pid])
