"""Article 8 team round-robin scope — format/criterion eligibility.

C.07 *Play-Off and Tie-Break Regulations* effective 1 March 2026,
Article 8 (*"Buchholz and other Tie-Breaks related to Buchholz"*) opens
with:

    Note: These tie-breaks must not be used in round-robins.

Article 8 covers §8.1 BH, §8.2 AOB and §8.3 FB.  Article 13 states that
tie-breaks described in Articles 6–10, or variations of them, may also
be applied to teams, so the restriction reaches the team forms of those
criteria.  SSSC is included because §13.4.2 defines its schedule
strength as "Buchholz of the team".

The team data model (``TeamRecord``/``TeamMatch``/``TeamFormat``) has no
tournament-format field.  The library therefore cannot *infer* a format,
and does not: ``mode=None`` means "not declared", and the Article-8
restriction is then not evaluated.  That is deliberately not the same as
assuming Swiss — it is documented and pinned by test.

Enforcement sits in the ruleset-aware conformance layer
(``strict.calculate_team_strict`` / ``rank_teams_strict``).  The raw
``team.calculate_team`` engine stays callable for custom and non-FIDE
calculations.
"""

import pytest

from tiebreak_core import calculate_team_strict, rank_teams_strict
from tiebreak_core.errors import (
    InvalidPlayerDataError,
    NotPermittedForFormatError,
)
from tiebreak_core.team import (
    TeamFormat,
    TeamMatch,
    TeamRecord,
    calculate_team,
)

# Article 8 (Buchholz family) — prohibited in round-robins.
RR_FORBIDDEN_TEAM_DESCRIPTORS = (
    "BH:MP", "BH:GP", "BH:MP/C1", "FB:MP", "FB:GP",
    "AOB:MP", "AOB:GP", "AOB:MP/F", "AOB:GP/F",
    "SSSC", "SSSC/F", "SSSC/K4",
)

# Article 9 (SB/KS), Article 6 (DE), Article 7 (WIN/WON/PS),
# Article 12 (BC/TBR/BBE), §13.1 (MPvGP), §13.2 (ESB) — permitted.
RR_PERMITTED_TEAM_SCALARS = (
    "EMMSB", "EMGSB", "EGMSB", "EGGSB",
    "EMMSB/C1", "EMMSB/P", "KS:MP", "KS:GP", "WIN:MP", "PS:MP", "PS:GP",
    "BC", "TBR", "BBE", "MPvGP",
)

# Article 6 group stages — ranking-only, so they are exercised through
# ``rank_teams_strict`` rather than the scalar entry point.
RR_PERMITTED_TEAM_STAGES = (
    "EDE", "EDEBT", "EDEBB", "EDET", "EDEB", "EDE/P",
)


def _teams():
    """Three teams, two rounds, board totals supplied (SSSC needs them)."""
    return {
        1: TeamRecord(1, 4.0, 5.5, [
            TeamMatch(2, 1, 2.0, 2.5), TeamMatch(3, 2, 2.0, 3.0)],
            (2.5, 3.0)),
        2: TeamRecord(2, 1.0, 2.5, [
            TeamMatch(1, 1, 0.0, 0.5), TeamMatch(3, 2, 1.0, 2.0)],
            (0.5, 2.0)),
        3: TeamRecord(3, 1.0, 3.0, [
            TeamMatch(1, 2, 0.0, 0.5), TeamMatch(2, 2, 1.0, 2.0)],
            (0.5, 2.5)),
    }


def _fmt():
    return TeamFormat()


# --- prohibited combinations ---------------------------------------------
@pytest.mark.parametrize("descriptor", RR_FORBIDDEN_TEAM_DESCRIPTORS)
def test_team_descriptor_refused_in_rr(descriptor):
    teams = _teams()
    with pytest.raises(NotPermittedForFormatError):
        calculate_team_strict(teams[1], teams, descriptor, 2,
                              _fmt(), mode="round_robin")


@pytest.mark.parametrize("descriptor", RR_FORBIDDEN_TEAM_DESCRIPTORS)
def test_team_ranking_refused_in_rr(descriptor):
    teams = _teams()
    with pytest.raises(NotPermittedForFormatError):
        rank_teams_strict(teams, [descriptor], 2, _fmt(),
                          mode="round_robin")


def test_team_ranking_list_refused_as_a_whole():
    """A permitted stage followed by a prohibited one still fails."""
    teams = _teams()
    with pytest.raises(NotPermittedForFormatError):
        rank_teams_strict(teams, ["MPvGP", "SSSC"], 2, _fmt(),
                          mode="round_robin")


# --- permitted combinations ----------------------------------------------
@pytest.mark.parametrize("descriptor", RR_PERMITTED_TEAM_SCALARS)
def test_team_descriptor_allowed_in_rr(descriptor):
    """ESB/KS/WIN/PS/BC/TBR/BBE/MPvGP are not Article 8."""
    teams = _teams()
    value = calculate_team_strict(teams[1], teams, descriptor, 2, _fmt(),
                                  mode="round_robin")
    assert isinstance(value, float)


@pytest.mark.parametrize("descriptor", RR_PERMITTED_TEAM_STAGES)
def test_team_group_stage_allowed_in_rr(descriptor):
    """Article 6 (DE and its chains) is not Article 8."""
    teams = _teams()
    assert rank_teams_strict(teams, [descriptor], 2, _fmt(),
                             mode="round_robin") is not None


@pytest.mark.parametrize("descriptor", RR_FORBIDDEN_TEAM_DESCRIPTORS)
def test_team_descriptor_allowed_in_swiss(descriptor):
    """The prohibition is format-scoped, not criterion-scoped."""
    teams = _teams()
    assert isinstance(
        calculate_team_strict(teams[1], teams, descriptor, 2, _fmt(),
                              mode="swiss"), float)


# --- undeclared format is not a Swiss assumption ------------------------
@pytest.mark.parametrize("descriptor", RR_FORBIDDEN_TEAM_DESCRIPTORS)
def test_undeclared_format_does_not_apply_the_restriction(descriptor):
    """``mode=None`` means "not declared", not "Swiss".

    The restriction is not evaluated — which is the documented
    behaviour, and is pinned here so it cannot drift into a silent
    assumption without this test changing.
    """
    teams = _teams()
    assert isinstance(
        calculate_team_strict(teams[1], teams, descriptor, 2, _fmt()),
        float)


def test_undeclared_format_does_not_reject_a_ranking():
    teams = _teams()
    result = rank_teams_strict(teams, ["MPvGP", "SSSC"], 2, _fmt())
    assert result is not None


def test_invalid_mode_is_rejected():
    teams = _teams()
    with pytest.raises(InvalidPlayerDataError):
        calculate_team_strict(teams[1], teams, "BH:MP", 2, _fmt(),
                              mode="round-robin")


# --- calculation vs eligibility -------------------------------------------
@pytest.mark.parametrize("descriptor", RR_FORBIDDEN_TEAM_DESCRIPTORS)
def test_raw_team_engine_still_computes_in_rr(descriptor):
    """Eligibility is a conformance rule; the team arithmetic stays."""
    teams = _teams()
    assert isinstance(calculate_team(teams[1], teams, descriptor, 2,
                                     _fmt()), float)
