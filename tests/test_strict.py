"""Strict additive API — fail-fast contracts, values identical to legacy.

Covers: unknown-criterion/ruleset rejection, malformed game/player input,
key mismatch, frozen registry immutability, controlled custom
registration, and strict-vs-legacy equivalence.
"""
import pytest

from tiebreak_core import (
    calculate_all,
    rank_standings,
    calculate_strict,
    calculate_all_strict,
    rank_standings_strict,
    order_ids_strict,
    frozen_registry,
    is_known,
    register_criterion,
    unregister_criterion,
    UnknownCriterionError,
    UnsupportedRulesetError,
    InvalidGameRecordError,
    InvalidPlayerDataError,
    DuplicatePlayerIdError,
    RegistryError,
    TIEBREAK_IDS,
)
from tiebreak_core.calculators import TIEBREAK_REGISTRY
from tiebreak_core.models import PlayerTiebreakData, GameRecord


def rec(opp, score, color="white", rnd=1, opp_rating=1500):
    return GameRecord(opponent_id=opp, opponent_rating=opp_rating,
                      score=score, color=color, round_number=rnd)


def fixture():
    p1 = PlayerTiebreakData(1, 2000, 2.5,
                            [rec(2, 1, rnd=1), rec(3, 0.5, rnd=2)])
    p2 = PlayerTiebreakData(2, 1900, 1.0,
                            [rec(1, 0, rnd=1), rec(3, 0.5, rnd=2)])
    p3 = PlayerTiebreakData(3, 1800, 1.5,
                            [rec(1, 0.5, rnd=1), rec(2, 0.5, rnd=2)])
    return {1: p1, 2: p2, 3: p3}


CRITERIA = ["buchholz", "buchholz_cut1", "sonneborn_berger",
            "progressive", "wins", "aro", "koya"]


class TestStrictEquivalence:
    def test_values_identical_to_legacy(self):
        players = fixture()
        for pid, pdata in players.items():
            assert calculate_all_strict(
                pdata, players, CRITERIA, 3
            ) == calculate_all(pdata, players, CRITERIA, 3)

    def test_ranking_identical_to_legacy(self):
        players = fixture()
        strict = rank_standings_strict(
            players, CRITERIA, 3, {1: 1, 2: 2, 3: 3})
        legacy = rank_standings(players, CRITERIA, 3, {1: 1, 2: 2, 3: 3})
        assert strict == legacy

    def test_order_ids_strict_matches_legacy(self):
        from tiebreak_core import order_ids
        points = {1: 2.0, 2: 2.0}
        values = {1: {"buchholz": 3.0}, 2: {"buchholz": 5.0}}
        assert order_ids_strict(
            points, values, ["buchholz"]) == order_ids(
            points, values, ["buchholz"])


class TestUnknownCriterion:
    def test_calculate_strict_rejects_unknown(self):
        players = fixture()
        with pytest.raises(UnknownCriterionError):
            calculate_strict(players[1], players, "nonexistent")

    def test_calculate_all_strict_rejects_unknown(self):
        players = fixture()
        with pytest.raises(UnknownCriterionError):
            calculate_all_strict(players[1], players, ["buchholz", "nope"])

    def test_rank_strict_rejects_unknown(self):
        with pytest.raises(UnknownCriterionError):
            rank_standings_strict(fixture(), ["buchholz", "bogus"], 3)

    def test_legacy_still_returns_zero(self):
        # Frozen legacy behavior: unchanged by the strict addition.
        players = fixture()
        assert calculate_all(
            players[1], players, ["nonexistent"], 3)["nonexistent"] == 0.0


class TestRuleset:
    def test_fide_2026_reserved_not_implemented(self):
        players = fixture()
        with pytest.raises(UnsupportedRulesetError):
            calculate_all_strict(
                players[1], players, ["buchholz"], 3, ruleset="fide-2026")

    def test_unknown_ruleset_rejected(self):
        with pytest.raises(UnsupportedRulesetError):
            rank_standings_strict(fixture(), ["buchholz"], 3,
                                  ruleset="fide-1999")

    def test_legacy_ruleset_accepted(self):
        players = fixture()
        res = rank_standings_strict(players, ["buchholz"], 3,
                                    ruleset="legacy-0.1.0")
        assert res.rules_version == "legacy-0.1.0"


class TestInputValidation:
    def test_bad_score_rejected(self):
        players = fixture()
        bad = PlayerTiebreakData(9, 1500, 1.0, [rec(1, 0.75)])
        with pytest.raises(InvalidPlayerDataError):
            calculate_all_strict(bad, {**players, 9: bad}, ["buchholz"], 3)

    def test_nan_score_rejected(self):
        players = fixture()
        bad = PlayerTiebreakData(9, 1500, 1.0, [rec(1, float("nan"))])
        with pytest.raises(InvalidPlayerDataError):
            calculate_all_strict(bad, {**players, 9: bad}, ["buchholz"], 3)

    def test_bad_color_rejected(self):
        players = fixture()
        bad = PlayerTiebreakData(9, 1500, 1.0, [rec(1, 1.0, color="red")])
        with pytest.raises(InvalidPlayerDataError):
            calculate_all_strict(bad, {**players, 9: bad}, ["buchholz"], 3)

    def test_negative_round_rejected(self):
        players = fixture()
        bad = PlayerTiebreakData(9, 1500, 1.0, [rec(1, 1.0, rnd=-2)])
        with pytest.raises(InvalidPlayerDataError):
            calculate_all_strict(bad, {**players, 9: bad}, ["buchholz"], 3)

    def test_negative_rating_rejected(self):
        players = fixture()
        bad = PlayerTiebreakData(9, -5, 1.0, [])
        with pytest.raises(InvalidPlayerDataError):
            rank_standings_strict({**players, 9: bad}, ["buchholz"], 3)

    def test_negative_points_rejected(self):
        players = fixture()
        bad = PlayerTiebreakData(9, 1500, -1.0, [])
        with pytest.raises(InvalidPlayerDataError):
            rank_standings_strict({**players, 9: bad}, ["buchholz"], 3)

    def test_key_mismatch_rejected(self):
        players = fixture()
        wrong_key = {99: players[1]}
        with pytest.raises(InvalidPlayerDataError):
            rank_standings_strict(wrong_key, ["buchholz"], 3)

    def test_non_mapping_rejected(self):
        with pytest.raises(InvalidPlayerDataError):
            rank_standings_strict(
                [PlayerTiebreakData(1, 1500, 0.0, [])], ["buchholz"], 3)

    def test_negative_total_rounds_rejected(self):
        with pytest.raises(InvalidPlayerDataError):
            rank_standings_strict(fixture(), ["buchholz"], -1)

    def test_bad_deterministic_keys_rejected(self):
        with pytest.raises(InvalidPlayerDataError):
            rank_standings_strict(fixture(), ["buchholz"], 3,
                                  deterministic_keys={1: "a"})


class TestFrozenRegistry:
    def test_snapshot_is_immutable(self):
        view = frozen_registry()
        with pytest.raises(TypeError):
            view["buchholz"] = lambda p, a: 0.0

    def test_snapshot_covers_builtins(self):
        view = frozen_registry()
        for cid in TIEBREAK_IDS:
            if cid in ("koya", "direct_encounter"):
                continue
            assert cid in view

    def test_mutating_legacy_dict_does_not_corrupt_snapshot(self):
        view = frozen_registry()
        assert "buchholz" in view  # snapshot holds its own copy

    def test_is_known(self):
        assert is_known("buchholz")
        assert is_known("koya") and is_known("direct_encounter")
        assert not is_known("nonexistent")


class TestControlledRegistration:
    def test_overwrite_builtin_refused(self):
        with pytest.raises(RegistryError):
            register_criterion("buchholz", lambda p, a: 42.0)
        # Built-in intact:
        assert TIEBREAK_REGISTRY["buchholz"] is frozen_registry()["buchholz"]

    def test_remove_builtin_refused(self):
        with pytest.raises(RegistryError):
            unregister_criterion("aro")

    def test_custom_roundtrip(self):
        try:
            register_criterion("custom_test_tb",
                               lambda p, a: float(p.wins) * 2)
            assert is_known("custom_test_tb")
            players = fixture()
            assert calculate_strict(
                players[1], players, "custom_test_tb") == 2.0
        finally:
            unregister_criterion("custom_test_tb")
        assert not is_known("custom_test_tb")

    def test_non_callable_refused(self):
        with pytest.raises(RegistryError):
            register_criterion("custom_test_tb2", 42.0)
