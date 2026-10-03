"""Game-kind taxonomy — explicit unplayed-game semantics, legacy-safe.

Covers: vocabulary constants, normalization (explicit wins, legacy -1 ->
unplayed, real opponent -> played), strict validation of kinds and
kind/opponent consistency, and proof that legacy calculators ignore kind
(identical values with kinds set vs unset).
"""
import pytest

from tiebreak_core import (
    ABSENT,
    FORFEIT_LOSS,
    FORFEIT_WIN,
    GAME_KINDS,
    PAIRING_BYE,
    PLAYED,
    REQUESTED_BYE,
    UNPLAYED,
    VIRTUAL_KINDS,
    calculate,
    calculate_all,
    calculate_all_strict,
    normalize_kind,
    InvalidGameRecordError,
    InvalidPlayerDataError,
)
from tiebreak_core.models import GameRecord, PlayerTiebreakData


def rec(opp, score, rnd=1, kind=""):
    return GameRecord(opponent_id=opp, opponent_rating=1500, score=score,
                      color="white", round_number=rnd, kind=kind)


class TestVocabulary:
    def test_all_kinds_listed(self):
        assert set(GAME_KINDS) == {
            "played", "pairing_bye", "forfeit_win", "forfeit_loss",
            "requested_bye", "unplayed", "absent",
        }

    def test_virtual_kinds(self):
        assert set(VIRTUAL_KINDS) == {
            "pairing_bye", "requested_bye", "unplayed", "absent",
        }


class TestNormalization:
    def test_explicit_kind_wins(self):
        g = rec(-1, 1.0, kind=PAIRING_BYE)
        assert normalize_kind(g) == "pairing_bye"

    def test_legacy_sentinel_normalizes_to_unplayed(self):
        assert normalize_kind(rec(-1, 1.0)) == UNPLAYED

    def test_real_opponent_normalizes_to_played(self):
        assert normalize_kind(rec(2, 1.0)) == PLAYED


class TestStrictKindValidation:
    def players(self, game):
        p = PlayerTiebreakData(1, 1500, 1.0, [game])
        return p, {1: p}

    def test_each_kind_accepted(self):
        for kind, opp in [(PLAYED, 2), (PAIRING_BYE, -1),
                          (FORFEIT_WIN, 2), (FORFEIT_WIN, -1),
                          (FORFEIT_LOSS, 2), (FORFEIT_LOSS, -1),
                          (REQUESTED_BYE, -1), (UNPLAYED, -1),
                          (ABSENT, -1)]:
            p, allp = self.players(rec(opp, 1.0 if kind != FORFEIT_LOSS else 0.0,
                                      kind=kind))
            calculate_all_strict(p, allp, ["buchholz"], 1)

    def test_unknown_kind_rejected(self):
        p, allp = self.players(rec(-1, 1.0, kind="walkover"))
        with pytest.raises(InvalidPlayerDataError):
            calculate_all_strict(p, allp, ["buchholz"], 1)

    def test_played_with_sentinel_rejected(self):
        p, allp = self.players(rec(-1, 1.0, kind=PLAYED))
        with pytest.raises(InvalidPlayerDataError):
            calculate_all_strict(p, allp, ["buchholz"], 1)

    def test_bye_with_real_opponent_rejected(self):
        for kind in (PAIRING_BYE, REQUESTED_BYE, UNPLAYED, ABSENT):
            p, allp = self.players(rec(2, 1.0, kind=kind))
            with pytest.raises(InvalidPlayerDataError):
                calculate_all_strict(p, allp, ["buchholz"], 1)


class TestLegacyIgnoresKind:
    def test_values_identical_with_kinds_set(self):
        games_plain = [rec(-1, 1.0, rnd=1), rec(2, 1.0, rnd=2)]
        games_kind = [rec(-1, 1.0, rnd=1, kind=PAIRING_BYE),
                      rec(2, 1.0, rnd=2, kind=PLAYED)]
        mk = lambda gs: {1: PlayerTiebreakData(1, 1500, 2.0, gs),
                         2: PlayerTiebreakData(2, 1500, 1.0, [])}
        crit = ["buchholz", "buchholz_cut1", "sonneborn_berger",
                "progressive", "aro", "koya"]
        plain, kinded = mk(games_plain), mk(games_kind)
        assert (calculate_all(kinded[1], kinded, crit, 2)
                == calculate_all(plain[1], plain, crit, 2))
        assert calculate(kinded[1], kinded, "buchholz") == 2.0
