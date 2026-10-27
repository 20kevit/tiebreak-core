"""``/P`` (forfeits as played) scope — descriptor-by-descriptor audit.

Source of truth: TEC *Mandatory Tie-Breaks* (``MTB-240824.doc``, published
at https://tec.fide.com/2024/04/30/mandatory-tie-breaks/), Tables 1–3.  The
table marks ``/P`` with a filled circle only on

    individuals : DE, BH (+/C1 /C2 /M1 /M2), SB (+/C1 /C2), FB (+/C1 /C2 /M1 /M2)
    teams       : EMMSB, EMGSB, EGMSB, EGGSB (+/C1 /C2),
                  EDE, EDEBT, EDEBB, EDET, EDEB, SSSC

and explicitly does **not** mark it on AOB, KS, PS, WIN, WON, ARO, TPR,
PTP, APRO, APPO, REP, BC, TBR, BBE or MPvGP.

Three independent paths must agree, and none may be broader than the
specification:

* the descriptor grammar (``modifiers._check_combination``),
* the named-criterion path (``fide2026.calculate`` /
  ``fide2024.calculate`` via ``strict``), and
* the ranking path (``rank_descriptors`` / ``rank_standings``).
"""

import pytest

from tiebreak_core import (
    calculate_all_strict,
    calculate_descriptor_strict,
    calculate_strict,
    rank_descriptors_strict,
)
from tiebreak_core.errors import (
    InvalidDescriptorError,
    InvalidPlayerDataError,
    UnsupportedCriterionError,
)
from tiebreak_core.models import GameRecord as G
from tiebreak_core.models import PlayerTiebreakData as P

# --- /P bases, exactly as the TEC table marks them ------------------------
INDIVIDUAL_P_BASES = ("DE", "BH", "SB", "FB")
INDIVIDUAL_P_VARIANTS = {
    "BH": ("BH/P", "BH/C1/P", "BH/C2/P", "BH/M1/P", "BH/M2/P"),
    "SB": ("SB/P", "SB/C1/P", "SB/C2/P"),
    "FB": ("FB/P", "FB/C1/P", "FB/C2/P", "FB/M1/P", "FB/M2/P"),
    "DE": ("DE/P",),
}
TEAM_P_BASES = (
    "EMMSB/P", "EMGSB/P", "EGMSB/P", "EGGSB/P", "EMMSB/C1/P", "EMMSB/C2/P",
    "EDE/P", "EDEBT/P", "EDEBB/P", "EDET/P", "EDEB/P",
    "SSSC/P", "SSSC/C1/P", "SSSC/C2/P", "SSSC/K1/P",
)
TEAM_NON_P = ("BC/P", "TBR/P", "BBE/P", "MPVGP/P", "AOB/P", "REP/P")

INDIVIDUAL_NON_P = (
    "AOB/P", "KS/P", "PS/P", "WIN/P", "WON/P", "REP/P",
    "STD/P", "TPN/P", "RTNG/P", "ARO/P", "TPR/P", "PTP/P", "APRO/P",
    "APPO/P", "BPG/P", "BWG/P", "GE/P", "AOB/F/P",
)


def _pl():
    return {
        1: P(1, 2000, 2.0, [
            G(2, 1800, 1.0, "white", 1, "played"),
            G(3, 1700, 1.0, "white", 2, "forfeit_win", opponent_score=0.0)]),
        2: P(2, 1800, 0.0, [G(1, 2000, 0.0, "black", 1, "played")]),
        3: P(3, 1700, 0.0, [G(1, 2000, 0.0, "black", 2, "forfeit_loss")]),
    }


# -------------------------------------------------------------------------
# descriptor grammar
# -------------------------------------------------------------------------
@pytest.mark.parametrize("descriptor", sum(
    (v for k, v in INDIVIDUAL_P_VARIANTS.items() if k != "DE"), ()))
def test_descriptor_accepts_official_p_bases(descriptor):
    players = _pl()
    assert calculate_descriptor_strict(
        players[1], players, descriptor, 2, ruleset="fide-2026") is not None


def test_de_p_is_accepted_on_the_group_ranking_path():
    """DE is group-level, so its ``/P`` form is only reachable there."""
    players = _pl()
    ranked = rank_descriptors_strict(
        players, ["DE/P"], 2, ruleset="fide-2026")
    assert ranked is not None


@pytest.mark.parametrize("descriptor", INDIVIDUAL_NON_P)
def test_descriptor_rejects_non_p_individual_bases(descriptor):
    players = _pl()
    with pytest.raises((InvalidDescriptorError, UnsupportedCriterionError)):
        calculate_descriptor_strict(
            players[1], players, descriptor, 2, ruleset="fide-2026")


@pytest.mark.parametrize("descriptor", TEAM_P_BASES)
def test_team_descriptor_accepts_official_p_bases(descriptor):
    """The team grammar accepts exactly the rows the TEC table marks."""
    from tiebreak_core.modifiers import parse_descriptor
    spec = parse_descriptor(descriptor)
    assert spec.forfeits_played is True


@pytest.mark.parametrize("descriptor", TEAM_NON_P)
def test_team_descriptor_rejects_non_p_bases(descriptor):
    from tiebreak_core.modifiers import parse_descriptor
    with pytest.raises((InvalidDescriptorError, UnsupportedCriterionError)):
        parse_descriptor(descriptor)


# -------------------------------------------------------------------------
# named-criterion path must match the grammar
# -------------------------------------------------------------------------
FIDE2024_P_CRITERIA = ("buchholz", "sonneborn_berger", "fore_buchholz")
FIDE2024_NON_P_CRITERIA = ("aob", "koya")


@pytest.mark.parametrize("criterion", FIDE2024_P_CRITERIA)
def test_named_criterion_accepts_p_under_fide_2024(criterion):
    players = _pl()
    assert calculate_strict(
        players[1], players, criterion, 2, ruleset="fide-2024",
        forfeits_as_played=True) is not None


@pytest.mark.parametrize("criterion", FIDE2024_NON_P_CRITERIA)
def test_named_criterion_rejects_p_under_fide_2024(criterion):
    """AOB and KS are not /P bases (TEC Table 1) — refuse, do not ignore.

    Regression for the inconsistency where ``fide2024`` advertised both
    as ``/P`` criteria while the descriptor grammar rejected ``AOB/P``
    and ``KS/P``.
    """
    players = _pl()
    with pytest.raises(InvalidPlayerDataError):
        calculate_strict(players[1], players, criterion, 2,
                         ruleset="fide-2024", forfeits_as_played=True)


@pytest.mark.parametrize("criterion", FIDE2024_NON_P_CRITERIA)
def test_named_criterion_rejects_p_under_fide_2026(criterion):
    players = _pl()
    with pytest.raises(InvalidPlayerDataError):
        calculate_strict(players[1], players, criterion, 2,
                         ruleset="fide-2026", forfeits_as_played=True)


@pytest.mark.parametrize("criterion", FIDE2024_P_CRITERIA)
def test_named_criterion_accepts_p_under_fide_2026(criterion):
    players = _pl()
    assert calculate_strict(
        players[1], players, criterion, 2, ruleset="fide-2026",
        forfeits_as_played=True) is not None


# -------------------------------------------------------------------------
# the flag must change the result where /P is defined, and nowhere else
# -------------------------------------------------------------------------
def test_p_flag_changes_buchholz_and_is_refused_elsewhere():
    """``/P`` changes the BH family; AOB/KS refuse it outright.

    The 2-round fixture gives P1 a played win and a forfeit win.  Under
    ``/P`` the forfeit round is scored against the scheduled opponent
    (§16.3 adjusted score) instead of the §16.4 dummy, so BH changes.
    AOB and KS are not /P bases (TEC Table 1) and must not be affected
    by the flag at all — they refuse it.
    """
    players = _pl()
    plain = calculate_all_strict(players[1], players, ["buchholz"], 2,
                                 ruleset="fide-2024")["buchholz"]
    played = calculate_all_strict(players[1], players, ["buchholz"], 2,
                                  ruleset="fide-2024",
                                  forfeits_as_played=True)["buchholz"]
    assert plain != played

    for criterion in ("aob", "koya"):
        with pytest.raises(InvalidPlayerDataError):
            calculate_all_strict(players[1], players, [criterion], 2,
                                 ruleset="fide-2024",
                                 forfeits_as_played=True)

    # Without the flag the frozen fide-2024 semantics are unchanged:
    # P1's only OTB opponent is P2, whose adjusted score is 2.0.
    assert calculate_all_strict(
        players[1], players, ["aob"], 2, ruleset="fide-2024")["aob"] == 2.0


def test_p_flag_is_rejected_for_non_p_criteria_on_the_ranking_path():
    players = _pl()
    with pytest.raises((InvalidDescriptorError, InvalidPlayerDataError,
                        UnsupportedCriterionError)):
        rank_descriptors_strict(players, ["AOB/P"], 2, ruleset="fide-2026")
