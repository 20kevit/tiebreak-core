"""Descriptor dispatch must not leak one ruleset's arithmetic into another.

Regression for the ``calculate_descriptor_strict(..., ruleset="fide-2024")``
defect: the generic MTB26 modifier machine is a ``fide-2026`` construct,
but the wrapper accepted ``fide-2024`` and ran the 2026 engine on it. The
2024 ruleset has no §16.4.1/§16.4.2 dummy caps, so every scalar
descriptor with an unplayed round silently returned 2026 values (e.g. a
capped ``BH/C1`` dummy of ``draw_points * rounds`` instead of the
uncapped own score) while the named ``buchholz_cut1`` id returned the
correct 2024 value — two answers for one ruleset.

Fix: ``modifiers.calculate_descriptor`` takes a ``ruleset`` argument and
``fide-2024`` dispatches to the frozen 2024 engine (named combos only;
the 2026-only ids and the generic ``n >= 3`` machine raise
``UnsupportedCriterionError``).

Basis: C.07 §§8.1/9.1/14.1/16.4 (2024 vs 2026 dummy rule, D13).
"""
import pytest

from tiebreak_core import fide2024 as f24
from tiebreak_core import fide2026 as f26
from tiebreak_core.errors import (InvalidDescriptorError,
                                InvalidPlayerDataError,
                                UnsupportedCriterionError,)
from tiebreak_core.models import GameRecord, PlayerTiebreakData
from tiebreak_core.modifiers import calculate_descriptor
from tiebreak_core.strict import (
    calculate_all_strict,
    calculate_descriptor_strict,
)


def P(pid, rating, points, games):
    return PlayerTiebreakData(
        player_id=pid, rating=rating, points=points,
        games=[GameRecord(opponent_id=o, opponent_rating=0, score=s,
                          color=c, round_number=r, kind=k)
               for (o, s, c, r, k) in games])


@pytest.fixture()
def unplayed_event():
    """5-round Swiss event with pairing/requested byes and a forfeit.

    Points are coherent (points == sum of recorded round scores) so both
    engines accept it. Every scalar descriptor on player 1 has an
    unplayed round, which is where the 2024 (uncapped dummy) and 2026
    (capped dummy) rules diverge.
    """
    return {
        1: P(1, 2000, 3.5, [(2, 1.0, "white", 1, "played"),
                            (-1, 1.0, "white", 2, "pairing_bye"),
                            (3, 1.0, "black", 3, "forfeit_win"),
                            (-1, 0.5, "white", 4, "requested_bye"),
                            (4, 0.0, "black", 5, "played")]),
        2: P(2, 1900, 1.0, [(1, 0.0, "black", 1, "played"),
                            (3, 0.5, "white", 2, "played"),
                            (4, 0.5, "black", 3, "played"),
                            (-1, 0.0, "white", 4, "requested_bye"),
                            (-1, 0.0, "white", 5, "requested_bye")]),
        3: P(3, 1800, 2.5, [(4, 1.0, "white", 1, "played"),
                            (2, 0.5, "black", 2, "played"),
                            (-1, 0.0, "white", 3, "forfeit_loss"),
                            (1, 1.0, "white", 4, "played"),
                            (-1, 0.0, "black", 5, "requested_bye")]),
        4: P(4, 1700, 2.0, [(3, 0.0, "black", 1, "played"),
                            (-1, 1.0, "white", 2, "pairing_bye"),
                            (1, 1.0, "white", 5, "played"),
                            (2, 0.0, "white", 4, "forfeit_loss"),
                            (-1, 0.0, "black", 3, "requested_bye")]),
    }


#: (descriptor, fide-2024 named id) pairs the 2024 ruleset publishes.
_FIDE2024_NAMED = [
    ("BH", "buchholz"),
    ("BH/C1", "buchholz_cut1"),
    ("BH/C2", "buchholz_cut2"),
    ("BH/M1", "median_buchholz"),
    ("BH/M2", "median_buchholz_2"),
    ("SB", "sonneborn_berger"),
    ("SB/C1", "sonneborn_berger_cut1"),
    ("PS", "progressive"),
    ("PS/C1", "progressive_cut1"),
    ("ARO", "aro"),
    ("ARO/C1", "aro_cut1"),
    ("FB", "fore_buchholz"),
    ("AOB", "aob"),
]

#: Descriptors the 2024 ruleset does not define (2026-only ids and the
#: generic ``n >= 3`` machine). (``SB/M1``/``SB/M2`` are not even
#: valid MTB26 descriptors — the grammar rejects them at parse time.)
_FIDE2024_UNSUPPORTED = [
    "BH/C3", "BH/M3", "SB/C2", "PS/C2", "PS/C3",
    "ARO/C2", "ARO/M1", "ARO/M2", "FB/C1", "FB/C2", "FB/M1", "FB/M2",
    "AOB/F",
]


class TestFide2024DescriptorDispatch:
    @pytest.mark.parametrize("descriptor,named", _FIDE2024_NAMED)
    def test_delegates_to_fide2024_engine(self, unplayed_event,
                                          descriptor, named):
        for pid in unplayed_event:
            got = calculate_descriptor_strict(
                unplayed_event[pid], unplayed_event, descriptor, 5,
                ruleset="fide-2024")
            want = f24.FIDE2024_REGISTRY[named](
                unplayed_event[pid], dict(unplayed_event), 5)
            assert got == pytest.approx(want)

    @pytest.mark.parametrize("descriptor,named", _FIDE2024_NAMED)
    def test_matches_calculate_all_strict_same_ruleset(
            self, unplayed_event, descriptor, named):
        for pid in unplayed_event:
            got = calculate_descriptor_strict(
                unplayed_event[pid], unplayed_event, descriptor, 5,
                ruleset="fide-2024")
            want = calculate_all_strict(
                unplayed_event[pid], unplayed_event, [named], 5,
                ruleset="fide-2024")[named]
            assert got == pytest.approx(want)

    @pytest.mark.parametrize("descriptor", _FIDE2024_UNSUPPORTED)
    def test_unsupported_descriptors_raise(self, unplayed_event, descriptor):
        for pid in unplayed_event:
            with pytest.raises(UnsupportedCriterionError):
                calculate_descriptor_strict(
                    unplayed_event[pid], unplayed_event, descriptor, 5,
                    ruleset="fide-2024")

    def test_koya_limit_descriptor(self, unplayed_event):
        # §14.5 /L±n: the half-point offset maps to the 2024 koya limit.
        for pid in unplayed_event:
            got = calculate_descriptor_strict(
                unplayed_event[pid], unplayed_event, "KS/L+1", 5,
                ruleset="fide-2024")
            want = f24.koya(unplayed_event[pid], dict(unplayed_event), 5,
                            koya_limit=0.5)
            assert got == pytest.approx(want)
            got_neg = calculate_descriptor_strict(
                unplayed_event[pid], unplayed_event, "KS/L-2", 5,
                ruleset="fide-2024")
            want_neg = f24.koya(unplayed_event[pid], dict(unplayed_event), 5,
                               koya_limit=-1.0)
            assert got_neg == pytest.approx(want_neg)

    def test_p_flag_counts_forfeits_as_played_under_fide_2024(self):
        """MTB26 ``/P`` under fide-2024 (§15.2 / §16.6), not a no-op.

        3 players, 3 rounds. P1 plays R1 (win vs P2), takes a forfeit
        win vs P3 in R2 and a pairing bye in R3. adj(P2) = 2.0,
        adj(P3) = 1.0, P1 own points = 3.0.

        Plain BH substitutes the §16.4 dummy (own points) for both
        unplayed rounds: 2.0 + 3.0 + 3.0 = 8.0. ``/P`` counts the
        forfeit as a played game against the scheduled opponent, so
        R2 contributes adj(P3) = 1.0 instead: 2.0 + 1.0 + 3.0 = 6.0.
        """
        pl = {
            1: P(1, 2000, 3.0, [(2, 1.0, "white", 1, "played"),
                                (3, 1.0, "white", 2, "forfeit_win"),
                                (-1, 1.0, "white", 3, "pairing_bye")]),
            2: P(2, 1900, 2.0, [(1, 0.0, "black", 1, "played"),
                                (-1, 1.0, "white", 2, "pairing_bye"),
                                (3, 1.0, "white", 3, "played")]),
            3: P(3, 1800, 1.0, [(-1, 1.0, "white", 1, "pairing_bye"),
                                (1, 0.0, "black", 2, "forfeit_loss"),
                                (2, 0.0, "black", 3, "played")]),
        }
        plain = calculate_descriptor_strict(pl[1], pl, "BH", 3,
                                            ruleset="fide-2024")
        assert plain == pytest.approx(8.0)
        flagged = calculate_descriptor_strict(pl[1], pl, "BH/P", 3,
                                              ruleset="fide-2024")
        assert flagged == pytest.approx(6.0)
        # The named-criterion path must agree with the descriptor path
        # (they previously disagreed: one rejected /P, one ignored it).
        assert flagged == pytest.approx(
            calculate_all_strict(pl[1], pl, ["buchholz"], 3,
                                 ruleset="fide-2024",
                                 forfeits_as_played=True)["buchholz"])
        assert flagged == pytest.approx(
            f24.buchholz(pl[1], dict(pl), 3, forfeits_as_played=True))

    def test_p_flag_undefined_for_ratings_and_type_b(self, unplayed_event):
        """``/P`` is not defined for ARO/PS/REP under fide-2024.

        §15.2 keeps forfeits unplayed in ratings-based (Article 10) and
        Type-B (Article 7) counts. The MTB26 grammar rejects the
        combination outright; the named-criterion path (which takes a
        boolean, not a descriptor) fails fast instead of ignoring it.
        """
        for descriptor in ("ARO/P", "PS/P", "REP/P"):
            with pytest.raises(InvalidDescriptorError):
                calculate_descriptor_strict(
                    unplayed_event[1], unplayed_event, descriptor, 5,
                    ruleset="fide-2024")
        for criterion in ("aro", "progressive", "rounds_elected"):
            with pytest.raises(InvalidPlayerDataError):
                calculate_all_strict(unplayed_event[1], unplayed_event,
                                     [criterion], 5, ruleset="fide-2024",
                                     forfeits_as_played=True)

    def test_team_and_stage_descriptors_raise(self, unplayed_event):
        for descriptor in ("BH:MP", "DE", "TPN", "RTNG"):
            with pytest.raises(UnsupportedCriterionError):
                calculate_descriptor_strict(
                    unplayed_event[1], unplayed_event, descriptor, 5,
                    ruleset="fide-2024")


class TestFide2024Vs2026Divergence:
    """The exact defect signature: same ruleset, two different answers."""

    def test_bh_cut1_uncapped_under_2024(self):
        # Player 1: 9 played wins vs #2 plus one pairing bye, 10 rounds.
        # 2024 §16.4: the unplayed dummy concludes on the player's own
        # points (10.0) — no §16.4.2 cap.
        players = {
            1: P(1, 2000, 10.0,
                 [(2, 1.0, "white", r, "played") for r in range(1, 10)]
                 + [(-1, 1.0, "white", 10, "pairing_bye")]),
            2: P(2, 1500, 0.0,
                 [(1, 0.0, "black", r, "played") for r in range(1, 10)]),
        }
        assert calculate_descriptor_strict(
            players[1], players, "BH/C1", 10, ruleset="fide-2024") == \
            pytest.approx(10.0)
        # 2026 §16.4.2 caps the dummy at draw_points * rounds = 5.0.
        assert calculate_descriptor_strict(
            players[1], players, "BH/C1", 10) == pytest.approx(5.0)
        assert calculate_descriptor_strict(
            players[1], players, "BH/C1", 10, ruleset="fide-2024") != \
            calculate_descriptor_strict(players[1], players, "BH/C1", 10)

    def test_every_scalar_descriptor_agrees_with_named_id(
            self, unplayed_event):
        # The named-id path never had the bug; the descriptor path must
        # now agree with it under the same ruleset.
        for pid in unplayed_event:
            for descriptor, named in _FIDE2024_NAMED:
                got = calculate_descriptor_strict(
                    unplayed_event[pid], unplayed_event, descriptor, 5,
                    ruleset="fide-2024")
                want = calculate_all_strict(
                    unplayed_event[pid], unplayed_event, [named], 5,
                    ruleset="fide-2024")[named]
                assert got == pytest.approx(want), (descriptor, named)


class TestFide2026DescriptorUnchanged:
    """The default (fide-2026) path keeps its frozen behaviour."""

    @pytest.mark.parametrize("descriptor,named", [
        ("BH", "buchholz"),
        ("BH/C1", "buchholz_cut1"),
        ("BH/C2", "buchholz_cut2"),
        ("BH/M1", "median_buchholz"),
        ("BH/M2", "median_buchholz_2"),
        ("SB", "sonneborn_berger"),
        ("SB/C1", "sonneborn_berger_cut1"),
        ("SB/C2", "sonneborn_berger_cut2"),
        ("PS", "progressive"),
        ("PS/C1", "progressive_cut1"),
        ("ARO", "aro"),
        ("ARO/C1", "aro_cut1"),
        ("ARO/C2", "aro_cut2"),
        ("FB", "fore_buchholz"),
        ("FB/C1", "fore_buchholz_cut1"),
        ("FB/M1", "fore_median1"),
        ("AOB", "aob"),
        ("AOB/F", "aob_fb"),
    ])
    def test_default_delegates_to_fide2026_engine(
            self, unplayed_event, descriptor, named):
        for pid in unplayed_event:
            got = calculate_descriptor_strict(
                unplayed_event[pid], unplayed_event, descriptor, 5)
            want = f26.FIDE2026_REGISTRY[named](
                unplayed_event[pid], dict(unplayed_event), 5, "swiss",
                0.5, False)
            assert got == pytest.approx(want)

    def test_generic_n_ge_3_still_works_under_fide_2026(
            self, unplayed_event):
        # Player 1's five BH elements (2026, Swiss): adj(2)=2.0,
        # pairing-bye dummy min(3.5, 0.5*5)=2.5, forfeit-win dummy
        # min(3.5, adj(3)=3.0)=3.0, requested-bye dummy 2.5, adj(4)=2.0.
        # BH/C3 applies §16.5.1 three times (VUR-preferential) and
        # leaves 2.5 + 3.0.
        got = calculate_descriptor_strict(
            unplayed_event[1], unplayed_event, "BH/C3", 5)
        assert got == pytest.approx(5.5)
        assert got < calculate_descriptor_strict(
            unplayed_event[1], unplayed_event, "BH", 5)


class TestModifiersRulesetArgument:
    def test_explicit_ruleset_argument(self, unplayed_event):
        for pid in unplayed_event:
            got = calculate_descriptor(
                unplayed_event[pid], unplayed_event, "BH/C1", 5,
                ruleset="fide-2024")
            assert got == pytest.approx(
                f24.buchholz_cut1(unplayed_event[pid],
                                  dict(unplayed_event), 5))
            got26 = calculate_descriptor(
                unplayed_event[pid], unplayed_event, "BH/C1", 5)
            assert got26 == pytest.approx(
                f26.buchholz_cut1(unplayed_event[pid],
                                  dict(unplayed_event), 5, "swiss", 0.5,
                                  False))

    def test_unknown_ruleset_argument_falls_back_to_2026(
            self, unplayed_event):
        # Only "fide-2024" is a distinct branch; anything else keeps the
        # generic 2026 machine (the strict wrapper validates the
        # vocabulary beforehand).
        got = calculate_descriptor(
            unplayed_event[1], unplayed_event, "BH/C1", 5,
            ruleset="fide-2026")
        assert got == pytest.approx(
            f26.buchholz_cut1(unplayed_event[1], dict(unplayed_event), 5,
                              "swiss", 0.5, False))
