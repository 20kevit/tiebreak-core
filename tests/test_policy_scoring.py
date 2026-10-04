"""Article-16 policy, scoring schemes, strict descriptor/team wrappers."""
import pytest

from tiebreak_core.article16 import (
    FIDE_2024_POLICY,
    FIDE_2026_RR_POLICY,
    FIDE_2026_SWISS_POLICY,
    resolve_policy,
)
from tiebreak_core.errors import (
    InvalidPlayerDataError,
    UnsupportedCriterionError,
)
from tiebreak_core import fide2024 as f24
from tiebreak_core import fide2026 as f26
from tiebreak_core.models import GameRecord, PlayerTiebreakData
from tiebreak_core.scoring import (
    STANDARD,
    ScoringScheme,
    is_standard,
    require_standard_or_explicit,
)
from tiebreak_core.strict import (
    calculate_descriptor_strict,
    calculate_team_strict,
    rank_descriptors_strict,
    rank_teams_strict,
)
from tiebreak_core.team import TeamFormat, TeamMatch, TeamRecord


def _mk(pid, rating, pts, games):
    return PlayerTiebreakData(
        player_id=pid, rating=rating, points=pts,
        games=[GameRecord(opponent_id=o, opponent_rating=r, score=s,
                          color=c, round_number=n, kind=k)
               for (o, r, s, c, n, k) in games])


@pytest.fixture()
def pair():
    return {
        1: _mk(1, 2000, 2.0, [(2, 1900, 1.0, "white", 1, "played"),
                              (2, 1900, 1.0, "white", 2, "played")]),
        2: _mk(2, 1900, 0.0, [(1, 2000, 0.0, "black", 1, "played"),
                              (1, 2000, 0.0, "black", 2, "played")]),
    }


# ------------------------------------------------------------------
# Article-16 policy resolution
# ------------------------------------------------------------------

def test_policy_defaults():
    assert resolve_policy("fide-2024") == FIDE_2024_POLICY
    assert resolve_policy("fide-2026") == FIDE_2026_SWISS_POLICY
    assert resolve_policy("fide-2026", mode="round_robin") == \
        FIDE_2026_RR_POLICY
    assert resolve_policy("fide-2026",
                          forfeits_as_played=True).forfeit_scope == \
        "as_played"
    assert FIDE_2024_POLICY.dummy_cap == "uncapped"
    assert FIDE_2026_SWISS_POLICY.dummy_cap == "capped"


def test_policy_overrides():
    custom = resolve_policy("fide-2026", late_bye_value=0.0)
    assert custom.late_bye_value == 0.0
    assert custom.dummy_cap == "capped"
    with pytest.raises(InvalidPlayerDataError):
        resolve_policy("fide-2026", late_bye_value=0.3)
    with pytest.raises(InvalidPlayerDataError):
        resolve_policy("fide-2026", nonexistent_flag=True)
    with pytest.raises(InvalidPlayerDataError):
        resolve_policy("legacy-0.1.0")
    with pytest.raises(InvalidPlayerDataError):
        resolve_policy("fide-2026", mode="knockout")


def test_default_policy_reproduces_engines(pair):
    # The resolved default policies describe the engines' behavior:
    # capped dummies only bite with unplayed rounds; fully-played
    # events agree across policies.
    assert f24.buchholz(pair[1], pair, 2) == \
        f26.buchholz(pair[1], pair, 2) == pytest.approx(0.0)
    assert resolve_policy("fide-2024").vur_cut_preference is True
    assert resolve_policy("fide-2026").reapply_cuts is True


# ------------------------------------------------------------------
# Scoring schemes
# ------------------------------------------------------------------

def test_scoring_scheme():
    assert is_standard(STANDARD)
    exotic = ScoringScheme(name="3-1-0", win=3.0, draw=1.0, loss=0.0)
    assert not is_standard(exotic)
    with pytest.raises(InvalidPlayerDataError):
        ScoringScheme(name="bad", win=0.5, draw=1.0, loss=0.0)
    # Standard without explicit score: caller derives complement.
    assert require_standard_or_explicit(STANDARD, None, "STD") is None
    assert require_standard_or_explicit(STANDARD, 1.0, "STD") == 1.0
    with pytest.raises(InvalidPlayerDataError):
        require_standard_or_explicit(exotic, None, "STD")
    assert require_standard_or_explicit(exotic, 2.0, "STD") == 2.0


# ------------------------------------------------------------------
# Strict descriptor wrappers
# ------------------------------------------------------------------

def test_descriptor_strict(pair):
    assert calculate_descriptor_strict(
        pair[1], pair, "BH/C1", 2) == pytest.approx(
            f26.buchholz_cut1(pair[1], pair, 2, "swiss", 0.5, False))
    assert calculate_descriptor_strict(
        pair[1], pair, "BH/C3", 2) == pytest.approx(
            f26.buchholz(pair[1], pair, 2, "swiss", 0.5, False))
    ranked = rank_descriptors_strict(pair, ["BH/C1", "DE"], 2)
    assert [p.player_id for p in ranked.players] == [1, 2]
    # Generic n>=3 under fide-2024: unsupported (named machine only).
    with pytest.raises(UnsupportedCriterionError):
        calculate_descriptor_strict(pair[1], pair, "BH/C3", 2,
                                    ruleset="fide-2024")
    # Named combo under fide-2024 works.
    assert calculate_descriptor_strict(
        pair[1], pair, "BH/C1", 2,
        ruleset="fide-2024") == pytest.approx(
            f24.buchholz_cut1(pair[1], pair, 2))
    # Team descriptors route to the team API.
    with pytest.raises(UnsupportedCriterionError):
        calculate_descriptor_strict(pair[1], pair, "BH:MP", 2)
    with pytest.raises(UnsupportedCriterionError):
        rank_descriptors_strict(pair, ["BH/C1"], 2, ruleset="fide-2024")


def _league():
    fmt = TeamFormat(mp_win=2.0, mp_draw=1.0)
    teams = {
        1: TeamRecord(1, 2.0, 3.0, [TeamMatch(2, 1, 2, 3.0)], (3.0,)),
        2: TeamRecord(2, 0.0, 1.0, [TeamMatch(1, 1, 0, 1.0)], (1.0,)),
    }
    return teams, fmt


def test_team_strict():
    teams, fmt = _league()
    assert calculate_team_strict(
        teams[1], teams, "EMMSB", 1, fmt) == pytest.approx(0.0)
    assert calculate_team_strict(
        teams[1], teams, "BH:MP", 1, fmt) == pytest.approx(0.0)
    ranked = rank_teams_strict(teams, ["EMMSB"], 1, fmt)
    assert [t.team_id for t in ranked.teams] == [1, 2]
    with pytest.raises(UnsupportedCriterionError):
        calculate_team_strict(teams[1], teams, "EDE", 1, fmt)
    with pytest.raises(InvalidPlayerDataError):
        rank_teams_strict({1: teams[1], 2: teams[2]}, ["EMMSB"], 0, fmt)
