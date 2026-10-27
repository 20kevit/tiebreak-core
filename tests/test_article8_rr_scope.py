"""Article 8 round-robin scope — tournament-format/criterion eligibility.

C.07 *Play-Off and Tie-Break Regulations* effective 1 March 2026,
Article 8 (*"Buchholz and other Tie-Breaks related to Buchholz"*) opens
with:

    Note: These tie-breaks must not be used in round-robins.

Article 8 covers BH (§8.1), AOB (§8.2) and FB (§8.3).  SB (§9.1) and KS
(§9.2) sit in Article 9 and are **not** restricted — KS is explicitly
titled "Koya System (for Round Robin)".

The 1 August 2024 edition of C.07 (the basis of the ``fide-2024``
ruleset) carries the same Article 8 text but **no such note**, so the
restriction is fide-2026-scoped only.

Eligibility is enforced by the ruleset-aware conformance interface
(``strict`` and the fide-2026 descriptor dispatch).  The raw engines stay
callable, so non-FIDE and custom rulesets keep the arithmetic.
"""

import pytest

from tiebreak_core import (
    calculate_all_strict,
    calculate_descriptor_strict,
    calculate_strict,
    rank_descriptors_strict,
    rank_standings_strict,
)
from tiebreak_core.errors import NotPermittedForFormatError
from tiebreak_core.models import GameRecord as G
from tiebreak_core.models import PlayerTiebreakData as P

# Article 8 (Buchholz family) — prohibited in round-robins under fide-2026.
RR_FORBIDDEN_CRITERIA = (
    "buchholz", "buchholz_cut1", "buchholz_cut2",
    "median_buchholz", "median_buchholz_2",
    "aob", "fore_buchholz", "fore_buchholz_cut1", "fore_buchholz_cut2",
    "fore_median1", "fore_median2",
)
RR_FORBIDDEN_DESCRIPTORS = ("BH", "BH/C1", "BH/C2", "BH/M1", "AOB", "AOB/F",
                            "FB", "FB/C1", "FB/P")

# Article 9 — permitted in round-robins (KS is explicitly an RR criterion).
RR_PERMITTED_CRITERIA = ("koya", "sonneborn_berger", "sonneborn_berger_cut1")
RR_PERMITTED_DESCRIPTORS = ("KS", "KS/L+1", "SB", "SB/C1", "SB/P", "DE/P")


def _pl():
    return {
        1: P(1, 2000, 2.0, [
            G(2, 1800, 1.0, "white", 1, "played"),
            G(3, 1700, 1.0, "white", 2, "played")]),
        2: P(2, 1800, 0.0, [G(1, 2000, 0.0, "black", 1, "played")]),
        3: P(3, 1700, 0.0, [G(1, 2000, 0.0, "black", 2, "played")]),
    }


# --- invalid combinations -------------------------------------------------
@pytest.mark.parametrize("criterion", RR_FORBIDDEN_CRITERIA)
def test_named_criterion_refused_in_rr_under_fide_2026(criterion):
    players = _pl()
    with pytest.raises(NotPermittedForFormatError):
        calculate_strict(players[1], players, criterion, 2,
                         ruleset="fide-2026", mode="round_robin")


@pytest.mark.parametrize("descriptor", RR_FORBIDDEN_DESCRIPTORS)
def test_descriptor_refused_in_rr_under_fide_2026(descriptor):
    players = _pl()
    with pytest.raises(NotPermittedForFormatError):
        calculate_descriptor_strict(players[1], players, descriptor, 2,
                                    ruleset="fide-2026", mode="round_robin")


@pytest.mark.parametrize("criterion", RR_FORBIDDEN_CRITERIA)
def test_ranking_refused_in_rr_under_fide_2026(criterion):
    players = _pl()
    with pytest.raises(NotPermittedForFormatError):
        rank_standings_strict(players, [criterion], 2, ruleset="fide-2026",
                              mode="round_robin")


@pytest.mark.parametrize("descriptor", RR_FORBIDDEN_DESCRIPTORS)
def test_rank_descriptors_refused_in_rr_under_fide_2026(descriptor):
    players = _pl()
    with pytest.raises(NotPermittedForFormatError):
        rank_descriptors_strict(players, [descriptor], 2,
                                ruleset="fide-2026", mode="round_robin")


def test_mixed_ranking_list_refused_as_a_whole():
    """A permitted criterion followed by a prohibited one still fails."""
    players = _pl()
    with pytest.raises(NotPermittedForFormatError):
        rank_standings_strict(players, ["koya", "buchholz"], 2,
                              ruleset="fide-2026", mode="round_robin")


# --- valid combinations ---------------------------------------------------
@pytest.mark.parametrize("criterion", RR_PERMITTED_CRITERIA)
def test_article9_criteria_allowed_in_rr(criterion):
    players = _pl()
    assert calculate_strict(players[1], players, criterion, 2,
                            ruleset="fide-2026", mode="round_robin") is not None


@pytest.mark.parametrize("descriptor", RR_PERMITTED_DESCRIPTORS)
def test_article9_descriptors_allowed_in_rr(descriptor):
    players = _pl()
    if descriptor.startswith("DE"):
        ranked = rank_descriptors_strict(players, [descriptor], 2,
                                         ruleset="fide-2026",
                                         mode="round_robin")
        assert ranked is not None
        return
    assert calculate_descriptor_strict(players[1], players, descriptor, 2,
                                       ruleset="fide-2026",
                                       mode="round_robin") is not None


@pytest.mark.parametrize("criterion", RR_FORBIDDEN_CRITERIA)
def test_all_criteria_allowed_in_swiss(criterion):
    """The prohibition is format-scoped, not criterion-scoped."""
    players = _pl()
    assert calculate_strict(players[1], players, criterion, 2,
                            ruleset="fide-2026", mode="swiss") is not None


# --- ruleset scope --------------------------------------------------------
#: The fide-2024 registry is a subset; the rest are 2026-only ids.
from tiebreak_core import fide2024 as _f24
from tiebreak_core.errors import InvalidPlayerDataError

FIDE2024_RR_CRITERIA = tuple(
    c for c in RR_FORBIDDEN_CRITERIA if c in set(_f24.FIDE2024_IDS))


@pytest.mark.parametrize("criterion", FIDE2024_RR_CRITERIA)
def test_fide_2024_has_no_article8_rr_note(criterion):
    """The 1 Aug 2024 edition's Article 8 carries no such prohibition.

    ``fide-2024`` has no format dimension at all: ``mode`` is a
    fide-2026 parameter, refused by ``strict``, and ``fide2024.calculate``
    takes no ``mode``.  The 1 Aug 2024 Article 8 therefore cannot give
    rise to a round-robin restriction, and the engine computes normally.
    """
    from tiebreak_core import fide2024
    players = _pl()
    assert fide2024.calculate(players[1], players, criterion, 2) is not None
    with pytest.raises((InvalidPlayerDataError, TypeError)):
        calculate_strict(players[1], players, criterion, 2,
                         ruleset="fide-2024", mode="round_robin")


#: Within the fide-2024 descriptor scope (generic /C1 /C2 /M1 and /F are
#: 2026-only per R1), these are all reachable in round-robin mode.
FIDE2024_RR_DESCRIPTORS = ("BH", "BH/C1", "BH/C2", "BH/M1", "AOB", "FB",
                           "FB/P")


@pytest.mark.parametrize("descriptor", FIDE2024_RR_DESCRIPTORS)
def test_fide_2024_descriptors_allowed_in_rr(descriptor):
    players = _pl()
    assert calculate_descriptor_strict(players[1], players, descriptor, 2,
                                       ruleset="fide-2024",
                                       mode="round_robin") is not None


# --- calculation vs eligibility -------------------------------------------
@pytest.mark.parametrize("criterion", RR_FORBIDDEN_CRITERIA)
def test_raw_engine_still_computes_in_rr(criterion):
    """Eligibility is a conformance rule; the arithmetic stays available."""
    from tiebreak_core import fide2026
    players = _pl()
    assert fide2026.calculate(players[1], players, criterion, 2,
                              "round_robin") is not None


def test_engine_rr_agrees_with_swiss_plus_p_flag():
    """``/P`` exists precisely to reproduce the RR arithmetic in Swiss."""
    from tiebreak_core import fide2026
    players = _pl()
    shared = dict(players)
    pre = fide2026._precompute(shared, 2, "round_robin", 0.5)
    assert (fide2026.buchholz(shared[1], shared, 2, "swiss", 0.5, True)
            == fide2026.buchholz(shared[1], shared, 2, "round_robin", 0.5,
                                 _pre=pre))
