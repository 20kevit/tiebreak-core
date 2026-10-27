"""Independent verification against the official FIDE Tie-Break Exercises.

Source: IA Mario Held, *Exercises in Tie-Breaking*, Rev. 2403220900 /
C.07-2023, FIDE Technical Commission
(`https://tec.fide.com/wp-content/uploads/2024/04/C.07-2023-Tiebreak-exercises-V01-1.pdf`).

The paper supplies a full 16-player Swiss crosstable and walks the
calculations by hand. Exercise 1 derives Buchholz for player #2 (Bruno)
as the plain sum of the opponents' scores:

    BH(#2) = 1.0 + 1.5 + 3.5 + 3.5 + 3.5 = 13.0

"Since neither the player nor any of the opponents have any unplayed
games, the basic Buchholz definition [8.1] applies, and no special
adjustments are required."

This module rebuilds that crosstable from the paper's own table (all 16
rows, transcribed independently of the library) and asserts the
published value. It is an *external* expected value: it comes from the
official document, not from this implementation.
"""
import pytest

from tiebreak_core import fide2026 as f26
from tiebreak_core.models import GameRecord as G
from tiebreak_core.models import PlayerTiebreakData as P

# (player_id, rating, score, [(opponent, result, colour, round, kind)])
# Result codes from the paper: + win, = draw, - loss; B = black, W = white.
# "BYE" = requested bye (the paper marks half-point and full-point byes
# alike); "F" = forfeit; a blank cell is an absent round (withdrawal).
_CROSSTABLE = [
    (2, 2150, 4.0, [(10, "+", "B", 1, "played"), (7, "+", "W", 2, "played"),
                    (1, "=", "B", 3, "played"), (16, "+", "W", 4, "played"),
                    (3, "=", "B", 5, "played")]),
    (1, 2200, 3.5, [(9, "+", "W", 1, "played"), (13, "=", "B", 2, "played"),
                    (2, "=", "W", 3, "played"), (15, "+", "B", 4, "played"),
                    (4, "=", "W", 5, "played")]),
    (3, 2100, 3.5, [(11, "=", "W", 1, "played"), (6, "+", "B", 2, "played"),
                    (8, "+", "W", 3, "played"), (4, "=", "B", 4, "played"),
                    (2, "=", "W", 5, "played")]),
    (4, 2050, 3.5, [(12, "+", "B", 1, "played"), (-1, "=", "W", 2, "bye"),
                    (13, "+", "W", 3, "played"), (3, "=", "W", 4, "played"),
                    (1, "=", "B", 5, "played")]),
    (16, 1450, 3.5, [(8, "=", "W", 1, "played"), (11, "+", "B", 2, "played"),
                     (7, "+", "W", 3, "played"), (2, "-", "B", 4, "played"),
                     (15, "+", "W", 5, "played")]),
    (6, 1950, 3.0, [(14, "-", "B", 1, "played"), (3, "-", "W", 2, "played"),
                    (-1, "+", "W", 3, "bye"), (10, "+", "W", 4, "played"),
                    (8, "+", "B", 5, "played")]),
    (5, 2000, 2.5, [(13, "-", "W", 1, "played"), (15, "-", "B", 2, "played"),
                    (11, "+", "W", 3, "played"), (7, "=", "B", 4, "played"),
                    (10, "+", "W", 5, "played")]),
    (8, 1850, 2.5, [(16, "=", "B", 1, "played"), (14, "+", "W", 2, "played"),
                    (3, "-", "B", 3, "played"), (13, "+", "W", 4, "played"),
                    (6, "-", "W", 5, "played")]),
    (11, 1700, 2.5, [(3, "=", "B", 1, "played"), (16, "-", "W", 2, "played"),
                     (5, "-", "B", 3, "played"), (9, "+", "W", 4, "forfeit_win"),
                     (7, "+", "W", 5, "played")]),
    (12, 1650, 2.0, [(4, "-", "W", 1, "played"), (-1, "+", "W", 2, "bye"),
                     (14, "+", "W", 3, "forfeit_win"),
                     (-1, "-", "W", 4, "absent"), (-1, "-", "W", 5, "absent")]),
    (14, 1550, 2.0, [(6, "+", "W", 1, "played"), (8, "-", "B", 2, "played"),
                     (12, "-", "W", 3, "forfeit_loss"),
                     (-1, "-", "W", 4, "absent"), (13, "+", "B", 5, "played")]),
    (15, 1500, 2.0, [(7, "-", "B", 1, "played"), (5, "+", "W", 2, "played"),
                     (10, "+", "B", 3, "played"), (1, "-", "W", 4, "played"),
                     (16, "-", "B", 5, "played")]),
    (7, 1900, 1.5, [(15, "+", "W", 1, "played"), (2, "-", "B", 2, "played"),
                    (16, "-", "B", 3, "played"), (5, "=", "W", 4, "played"),
                    (11, "-", "B", 5, "played")]),
    (9, 1800, 1.5, [(1, "-", "B", 1, "played"), (10, "-", "W", 2, "played"),
                    (-1, "=", "W", 3, "bye"), (11, "-", "W", 4, "forfeit_loss"),
                    (-1, "+", "W", 5, "bye")]),
    (13, 1600, 1.5, [(5, "+", "B", 1, "played"), (1, "=", "W", 2, "played"),
                     (4, "-", "B", 3, "played"), (8, "-", "B", 4, "played"),
                     (14, "-", "W", 5, "played")]),
    (10, 1750, 1.0, [(2, "-", "W", 1, "played"), (9, "+", "B", 2, "played"),
                     (15, "-", "W", 3, "played"), (6, "-", "B", 4, "played"),
                     (5, "-", "B", 5, "played")]),
]

_SCORE = {"+": 1.0, "=": 0.5, "-": 0.0}


def _swiss_crosstable():
    out = {}
    for pid, rating, points, games in _CROSSTABLE:
        recs = []
        for opp, res, colour, rnd, kind in games:
            if kind == "absent":
                recs.append(G(opp, 0, 0.0, colour, rnd, "absent"))
            elif kind == "bye":
                recs.append(G(opp, 0, _SCORE[res], colour, rnd,
                              "requested_bye"))
            elif kind == "forfeit_win":
                recs.append(G(opp, 0, 1.0, colour, rnd, "forfeit_win"))
            elif kind == "forfeit_loss":
                recs.append(G(opp, 0, 0.0, colour, rnd, "forfeit_loss"))
            else:
                recs.append(G(opp, 0, _SCORE[res], colour, rnd, "played"))
        out[pid] = P(pid, rating, points, recs)
    return out


class TestOfficialSwissCrosstable:
    def test_crosstable_is_coherent(self):
        """The transcribed table must reproduce every published score."""
        by_id = {row[0]: row for row in _CROSSTABLE}
        pl = _swiss_crosstable()
        for pid, _rating, points, games in _CROSSTABLE:
            total = sum(_SCORE[g[1]] for g in games if g[4] != "absent")
            assert total == pytest.approx(points), f"player {pid}"
        assert len(pl) == 16
        assert len(by_id) == 16

    def test_exercise_1_buchholz_total(self):
        """Exercise 1: BH(#2) = 13.0 (sum of opponents' scores)."""
        pl = _swiss_crosstable()
        assert f26.calculate(pl[2], pl, "buchholz", 5, "swiss") == \
            pytest.approx(13.0)

    def test_exercise_1_buchholz_is_unadjusted(self):
        """No opponent of #2 has an unplayed round, so adj == raw score."""
        pl = _swiss_crosstable()
        raw = sum(pl[opp].points for opp in (10, 7, 1, 16, 3))
        assert raw == pytest.approx(13.0)
        # ... and the library agrees with the raw sum, i.e. applies no
        # §16.3 adjustment on this fixture.
        assert f26.calculate(pl[2], pl, "buchholz", 5, "swiss") == \
            pytest.approx(raw)
