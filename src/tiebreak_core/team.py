"""
Team tie-break domain (C.07 Articles 11–13 + modifiers 14.1.2/14.2).

This module is deliberately separate from the individual ``GameRecord``
model: team events score matches in MP/GP with per-board vectors, and
stretching the individual record would corrupt both domains (see
``docs/ARCHITECTURE_GAP_ANALYSIS.md``).

Primary sources (retrieved October 2026; see ``docs/FIDE_SOURCE_REGISTRY.md``):

- FIDE Handbook C.07 (2026 ed., effective 1 Mar 2026; 2024 text
  ``2024_FC2_18`` where identical): §11 (MP/GP primitives), §12.1 BC
  ("multiply the board number by the number of game points achieved
  on that board ... The lower the sum ... the higher the ranking ...
  only ... same number of game points"), §12.2 TBR ("game points
  achieved on the first board ... If ... not decisive, reapply ...
  to the top most board not yet counted"), §12.3 BBE ("game points
  achieved on all boards except for the bottom board ... reapply to
  the bottom-most board not yet excluded"), §12 intro ("individual
  forfeit wins or losses are considered as standard wins or losses;
  ... pairing-allocated bye, the game points considered for each
  board are the same as those assigned to a standard win"), §13.1
  MPvGP, §13.2 ESB ("adding for each opponent a value given by the
  product of two elements: the total number of MP or GP achieved by
  the opponent ... the number of MP or GP scored against that
  [opponent]"; four combos EMMSB/EMGSB/EGMSB/EGGSB §§13.2.1–13.2.4),
  §13.3.1 EDE ("Apply the Direct Encounter rule (Article 6), first
  using the primary score ..., then, if no ties were broken ..., using
  the secondary score"), §13.3.2 chains (EDEBT/EDEBB/EDET/EDEB),
  §13.4 SSSC ("the secondary score ..." + "Schedule Strength ...
  division between [dividend] Buchholz of the team, based on the
  primary score (note: ... use Fore Buchholz [if needed before
  playing]) [and divisor] a normalising factor, given by the highest
  achievable primary score in the tournament divided by the highest
  secondary score achievable in a single match, rounded to the nearest
  integer towards zero, or by a different value"), §14.1.2 team ESB-C1
  ("exclude ... the contribution (product) associated with the
  opponent with the lowest MP score (for EMMSB and EMGSB) or GP score
  (for EGMSB and EGGSB) — if there is more than one such opponent,
  exclude the lowest contribution associated with them"), §13 blanket
  rule (Arts. 6–10 reusable for teams on an MP/GP reference score).
- MTB26 code table (variant permissions + chain names).

Evidence levels: every formula above is PRIMARY_NORMATIVE. Marked
PROJECT_DERIVED interpretations (documented at each site): unplayed
team matches in BH sums (own-total dummy, mirroring individual §16.4
uncapped — no team-specific dummy text was retrieved); ESB sums over
played matches only; team fore-BH (final-round played matches count
as drawn); EDE incomplete-meeting fallback (individual §6.3 certainty
on the primary score); chain stages applying inside exactly-two-team
groups per §13.3.2 wording. No official team worked example was
retrieved — tests are definition-derived (INDEPENDENT hand
calculation) plus property tests.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Mapping, Sequence, Tuple

from tiebreak_core.errors import (
    InvalidPlayerDataError,
    UnsupportedCriterionError,
)
from tiebreak_core.modifiers import ModifierSpec, parse_descriptor

# ------------------------------------------------------------------
# Data model
# ------------------------------------------------------------------

PLAYED = "played"
FORFEIT_WIN = "forfeit_win"
FORFEIT_LOSS = "forfeit_loss"
PAIRING_BYE = "pairing_bye"
UNPLAYED = "unplayed"

TEAM_KINDS: Tuple[str, ...] = (
    PLAYED, FORFEIT_WIN, FORFEIT_LOSS, PAIRING_BYE, UNPLAYED,
)

#: Kinds treated as contested matches (recorded MP/GP stand, counting
#: as regular matches — §12 intro for forfeits; consumer records
#: standard-win scores for PAB legs).
CONTESTED_KINDS = (PLAYED, FORFEIT_WIN, FORFEIT_LOSS)


@dataclass
class TeamMatch:
    """One team match from the perspective of one team."""

    opponent_id: int
    round_number: int
    mp: float  # match points scored (e.g. 2 / 1 / 0)
    gp: float  # game/board points scored
    kind: str = PLAYED


@dataclass
class TeamRecord:
    """All data needed for team tie-break calculation for one team."""

    team_id: int
    mp: float  # final match points
    gp: float  # final game points
    matches: List[TeamMatch] = field(default_factory=list)
    board_points: Tuple[float, ...] = ()
    # Tournament board totals: board_points[0] = GP on board 1 summed
    # over the event. Forfeit/PAB legs are included by the consumer
    # per the §12 intro (forfeits as standard wins/losses; PAB legs as
    # standard-win GP). Empty tuple = boards unknown (BC/TBR/BBE
    # unavailable — requesting them raises).


@dataclass(frozen=True)
class TeamFormat:
    """Event scoring parameters (consumer contract)."""

    mp_win: float = 2.0
    mp_draw: float = 1.0
    max_gp_per_match: float | None = None
    # Highest secondary score achievable in a single match. Defaults
    # to len(board_points) (one point per board) when a record
    # carries board totals; SSSC without any board information
    # requires this explicitly.


@dataclass(frozen=True)
class TeamResult:
    """Immutable per-team calculation result."""

    team_id: int
    mp: float
    gp: float
    values: Mapping[str, float] = field(default_factory=dict)
    rank: int = 0


@dataclass(frozen=True)
class TeamStandingsResult:
    """Immutable ordered team standings."""

    teams: Tuple[TeamResult, ...] = ()
    criteria: Tuple[str, ...] = ()
    rules_version: str = "fide-2026"


# ------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------

def validate_match(match: object, *, index: int = -1) -> None:
    from tiebreak_core.errors import InvalidGameRecordError

    if not isinstance(match, TeamMatch):
        raise InvalidGameRecordError(
            f"match[{index}]: expected TeamMatch, "
            f"got {type(match).__name__}")
    if isinstance(match.opponent_id, bool) or not isinstance(
            match.opponent_id, int):
        raise InvalidGameRecordError(
            f"match[{index}]: opponent_id must be int, "
            f"got {match.opponent_id!r}")
    for attr in ("mp", "gp"):
        value = getattr(match, attr)
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value < 0):
            raise InvalidGameRecordError(
                f"match[{index}]: {attr} must be a finite number >= 0, "
                f"got {value!r}")
    if (isinstance(match.round_number, bool) or not isinstance(
            match.round_number, int) or match.round_number < 0):
        raise InvalidGameRecordError(
            f"match[{index}]: round_number must be int >= 0, "
            f"got {match.round_number!r}")
    if match.kind not in TEAM_KINDS:
        raise InvalidGameRecordError(
            f"match[{index}]: kind must be one of {list(TEAM_KINDS)}, "
            f"got {match.kind!r}")
    if match.kind in (PAIRING_BYE, UNPLAYED) and match.opponent_id != -1:
        raise InvalidGameRecordError(
            f"match[{index}]: kind {match.kind!r} requires "
            f"opponent_id=-1, got {match.opponent_id!r}")


def validate_team(team: object) -> None:
    from tiebreak_core.errors import InvalidGameRecordError

    if not isinstance(team, TeamRecord):
        raise InvalidPlayerDataError(
            f"expected TeamRecord, got {type(team).__name__}")
    if isinstance(team.team_id, bool) or not isinstance(team.team_id, int):
        raise InvalidPlayerDataError(
            f"team_id must be int, got {team.team_id!r}")
    for attr in ("mp", "gp"):
        value = getattr(team, attr)
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value < 0):
            raise InvalidPlayerDataError(
                f"team {team.team_id}: {attr} must be a finite "
                f"number >= 0, got {value!r}")
    if not isinstance(team.matches, list):
        raise InvalidPlayerDataError(
            f"team {team.team_id}: matches must be a list")
    try:
        for i, match in enumerate(team.matches):
            validate_match(match, index=i)
    except InvalidGameRecordError as exc:
        raise InvalidPlayerDataError(
            f"team {team.team_id}: {exc}") from exc
    if not isinstance(team.board_points, tuple):
        raise InvalidPlayerDataError(
            f"team {team.team_id}: board_points must be a tuple")
    for i, value in enumerate(team.board_points):
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value < 0):
            raise InvalidPlayerDataError(
                f"team {team.team_id}: board_points[{i}] must be a "
                f"finite number >= 0, got {value!r}")


def validate_teams(
        teams: Mapping[int, TeamRecord]) -> Dict[int, TeamRecord]:
    if not isinstance(teams, Mapping):
        raise InvalidPlayerDataError(
            f"teams must be a mapping of id -> TeamRecord, "
            f"got {type(teams).__name__}")
    checked: Dict[int, TeamRecord] = {}
    for key, team in teams.items():
        if isinstance(key, bool) or not isinstance(key, int):
            raise InvalidPlayerDataError(
                f"team key must be int, got {key!r}")
        validate_team(team)
        if key != team.team_id:
            raise InvalidPlayerDataError(
                f"mapping key {key} != team.team_id {team.team_id}")
        checked[key] = team
    return checked


def _require_total_rounds(total_rounds: int) -> None:
    if (isinstance(total_rounds, bool) or not isinstance(total_rounds, int)
            or total_rounds < 1):
        raise InvalidPlayerDataError(
            f"team calculations require total_rounds >= 1, "
            f"got {total_rounds!r}")


def _require_primary(primary: str) -> str:
    if primary not in ("MP", "GP"):
        raise InvalidPlayerDataError(
            f"primary must be 'MP' or 'GP', got {primary!r}")
    return primary


def _secondary(primary: str) -> str:
    return "GP" if primary == "MP" else "MP"


def _total(team: TeamRecord, score: str) -> float:
    return team.mp if score == "MP" else team.gp


def _scored(match: TeamMatch, score: str) -> float:
    return match.mp if score == "MP" else match.gp


# ------------------------------------------------------------------
# Article 11 primitives + §13.1
# ------------------------------------------------------------------

def match_points(team: TeamRecord, all_teams: Mapping[int, TeamRecord],
                 total_rounds: int, fmt: TeamFormat,
                 primary: str = "MP") -> float:
    """§11.1.1 match points (stored final total)."""
    return float(team.mp)


def game_points(team: TeamRecord, all_teams: Mapping[int, TeamRecord],
                total_rounds: int, fmt: TeamFormat,
                primary: str = "MP") -> float:
    """§11.1.2 game points (stored final total)."""
    return float(team.gp)


def mpvgp(team: TeamRecord, all_teams: Mapping[int, TeamRecord],
          total_rounds: int, fmt: TeamFormat,
          primary: str = "MP") -> float:
    """§13.1: the score *other* than the primary (default MP -> GP)."""
    _require_primary(primary)
    return float(team.gp if primary == "MP" else team.mp)


# ------------------------------------------------------------------
# Team Buchholz (primary-score based; dividend for SSSC)
# ------------------------------------------------------------------

def team_buchholz(team: TeamRecord, all_teams: Mapping[int, TeamRecord],
                  total_rounds: int, fmt: TeamFormat,
                  primary: str = "MP", fore: bool = False) -> float:
    """Σ opponent final primary totals (played) + own-total dummies.

    Unplayed team rounds contribute the team's own final total as a
    dummy (PROJECT_DERIVED — mirrors individual §16.4 uncapped; no
    team-specific dummy text was retrieved). ``fore`` treats
    final-round played matches as drawn (PROJECT_DERIVED team-fore
    reading: MP draw value + half of max-GP per board leg).
    """
    _require_primary(primary)
    opp_totals = _opponent_totals(all_teams, primary, fore, total_rounds,
                                  fmt)
    total = 0.0
    for match in team.matches:
        if match.kind in CONTESTED_KINDS and match.opponent_id in all_teams:
            total += opp_totals[match.opponent_id]
        else:
            total += _total(team, primary)
    return total


def _opponent_totals(all_teams: Mapping[int, TeamRecord], score: str,
                     fore: bool, total_rounds: int,
                     fmt: TeamFormat) -> Dict[int, float]:
    if not fore:
        return {tid: _total(t, score) for tid, t in all_teams.items()}
    # Fore projection: final-round played matches count as drawn.
    out: Dict[int, float] = {}
    for tid, team in all_teams.items():
        value = _total(team, score)
        for match in team.matches:
            if (match.round_number == total_rounds
                    and match.kind in CONTESTED_KINDS):
                if score == "MP":
                    value += fmt.mp_draw - match.mp
                else:
                    boards = _boards(team, fmt)
                    value += boards * 0.5 - match.gp
        out[tid] = value
    return out


def _boards(team: TeamRecord, fmt: TeamFormat) -> int:
    if fmt.max_gp_per_match is not None:
        return int(fmt.max_gp_per_match)
    if team.board_points:
        return len(team.board_points)
    raise InvalidPlayerDataError(
        f"team {team.team_id}: board count unknown (no board_points, "
        f"no TeamFormat.max_gp_per_match) — required for GP fore/SSSC")


# ------------------------------------------------------------------
# Article 12 — knockout codes
# ------------------------------------------------------------------

def board_count(team: TeamRecord, all_teams: Mapping[int, TeamRecord],
                total_rounds: int, fmt: TeamFormat,
                primary: str = "MP") -> float:
    """§12.1 BC: Σ board_number × GP on that board. LOWER wins."""
    _require_boards(team)
    return sum((i + 1) * bp for i, bp in enumerate(team.board_points))


def _require_boards(team: TeamRecord) -> None:
    if not team.board_points:
        raise InvalidPlayerDataError(
            f"team {team.team_id}: board_points required for "
            f"BC/TBR/BBE")


def tbr_key(team: TeamRecord) -> Tuple[float, ...]:
    """§12.2 TBR: per-board GP from the top (descending compare)."""
    _require_boards(team)
    return tuple(float(bp) for bp in team.board_points)


def bbe_key(team: TeamRecord) -> Tuple[float, ...]:
    """§12.3 BBE: sums excluding bottom boards (descending compare).

    First element excludes the bottom board only; each further
    element excludes one more board upward (§12.3 reapplication).
    """
    _require_boards(team)
    boards = [float(bp) for bp in team.board_points]
    return tuple(sum(boards[:len(boards) - k])
                 for k in range(1, len(boards) + 1))


# ------------------------------------------------------------------
# Article 13.2 — Extended Sonneborn-Berger
# ------------------------------------------------------------------

#: ESB variant -> (opponent-total side, scored side).
_ESB_SIDES: Dict[str, Tuple[str, str]] = {
    "EMMSB": ("MP", "MP"),
    "EMGSB": ("MP", "GP"),
    "EGMSB": ("GP", "MP"),
    "EGGSB": ("GP", "GP"),
}


def esb(team: TeamRecord, all_teams: Mapping[int, TeamRecord],
        variant: str, total_rounds: int, fmt: TeamFormat,
        primary: str = "MP", cut: int = 0) -> float:
    """§13.2 ESB (+ §14.1.2 team C1, reapplied for C2).

    Per opponent: opponent final total (MP side for EMMSB/EMGSB, GP
    side for EGMSB/EGGSB) × points scored against them. Sums run over
    contested matches only (PROJECT_DERIVED — no unplayed-team text
    retrieved). The C1 victim is the product of the lowest-basis
    opponent (lowest contribution on ties); C2 reapplies (§16.5.2
    shape, documented).
    """
    if variant not in _ESB_SIDES:
        raise UnsupportedCriterionError(variant, "fide-2026")
    opp_side, scored_side = _ESB_SIDES[variant]
    elements: List[Tuple[float, float]] = []  # (basis, product)
    for match in team.matches:
        if (match.kind not in CONTESTED_KINDS
                or match.opponent_id not in all_teams):
            continue
        basis = _total(all_teams[match.opponent_id], opp_side)
        elements.append((basis, basis * _scored(match, scored_side)))
    if cut:
        if cut < 0 or cut > _MAX_TEAM_CUT:
            raise InvalidPlayerDataError(
                f"ESB cut out of range [0..{_MAX_TEAM_CUT}], got {cut}")
        for _ in range(min(cut, max(0, len(elements) - 1))):
            elements.pop(_esb_c1_victim(elements))
    return sum(value for _, value in elements)


_MAX_TEAM_CUT = 64


def _esb_c1_victim(elements: List[Tuple[float, float]]) -> int:
    low = min(basis for basis, _ in elements)
    low_val = min(value for basis, value in elements if basis == low)
    return next(i for i, (basis, value) in enumerate(elements)
                if basis == low and value == low_val)


# ------------------------------------------------------------------
# Article 13.4 — SSSC
# ------------------------------------------------------------------

def sssc(team: TeamRecord, all_teams: Mapping[int, TeamRecord],
         total_rounds: int, fmt: TeamFormat, primary: str = "MP",
         fore: bool = False, k: int | None = None) -> float:
    """§13.4 SSSC: secondary score + BH(primary) ÷ normaliser.

    Default normaliser: ``trunc(max_primary / max_secondary_per_match)``
    where max_primary = rounds × (mp_win | max_gp) and
    max_secondary_per_match = max_gp | mp_win. ``/Kx`` overrides it.
    """
    _require_primary(primary)
    _require_total_rounds(total_rounds)
    secondary = _secondary(primary)
    secondary_value = _total(team, secondary)
    if primary == "MP":
        max_primary = total_rounds * fmt.mp_win
        max_secondary = _max_gp(team, fmt)
    else:
        max_primary = total_rounds * _max_gp(team, fmt)
        max_secondary = fmt.mp_win
    divisor = k if k is not None else _trunc_div(max_primary,
                                                 max_secondary)
    if divisor < 1:
        raise InvalidPlayerDataError(
            f"SSSC normaliser must be >= 1, got {divisor} "
            f"(max_primary={max_primary}, "
            f"max_secondary_per_match={max_secondary})")
    return secondary_value + team_buchholz(team, all_teams, total_rounds,
                                           fmt, primary, fore) / divisor


def _max_gp(team: TeamRecord, fmt: TeamFormat) -> float:
    if fmt.max_gp_per_match is not None:
        return float(fmt.max_gp_per_match)
    if team.board_points:
        return float(len(team.board_points))
    raise InvalidPlayerDataError(
        f"team {team.team_id}: max GP per match unknown (no "
        f"board_points, no TeamFormat.max_gp_per_match)")


def _trunc_div(numerator: float, denominator: float) -> int:
    if denominator <= 0:
        raise InvalidPlayerDataError(
            f"SSSC normaliser needs a positive secondary maximum, "
            f"got {denominator}")
    return int(numerator / denominator)  # trunc toward zero (positive)


# ------------------------------------------------------------------
# Article 13.3 — Extended Direct Encounter (group-level)
# ------------------------------------------------------------------

def _mini_scores(group: Sequence[int],
                 teams: Mapping[int, TeamRecord],
                 score: str) -> Tuple[Dict[int, Fraction], Dict[int, int]]:
    """Head-to-head mini-standings over a tied team group.

    Contested mutual matches only; repeated meetings average per side
    (§6.1.2 shape). Returns (mini-scores, unplayed-pair counts).

    Pair iteration (F4, 1.2.0): each side's matches credit its own
    mini-score, so the table is independent of group order (prior
    code credited only the first-iterated side per pair).
    """
    mini: Dict[int, Fraction] = {tid: Fraction(0) for tid in group}
    missing: Dict[int, int] = {tid: 0 for tid in group}
    members = list(group)
    for idx, first in enumerate(members):
        for second in members[idx + 1:]:
            first_scs = [float(_scored(m, score))
                         for m in teams[first].matches
                         if m.opponent_id == second
                         and m.kind in CONTESTED_KINDS]
            second_scs = [float(_scored(m, score))
                          for m in teams[second].matches
                          if m.opponent_id == first
                          and m.kind in CONTESTED_KINDS]
            if first_scs:
                mini[first] += (sum(Fraction(v) for v in first_scs)
                               / len(first_scs))
            if second_scs:
                mini[second] += (sum(Fraction(v) for v in second_scs)
                                 / len(second_scs))
    for idx, first in enumerate(members):
        for second in members[idx + 1:]:
            met = any(m.opponent_id == second
                      for m in teams[first].matches) \
                or any(m.opponent_id == first
                       for m in teams[second].matches)
            if not met:
                missing[first] += 1
                missing[second] += 1
    return mini, missing


def _ede_tiers(group: Sequence[int],
               teams: Mapping[int, TeamRecord],
               primary: str, fmt: TeamFormat | None = None) -> List[List[int]]:
    """Resolve one tied team group per §13.3.1 (primary, then secondary).

    Complete meetings: mini-table order on the primary score; tied
    subsets reapply on the secondary score (§13.3.3 subset-restart
    shape). Incomplete meetings: §6.3-certainty analog on the primary
    score (PROJECT_DERIVED — C.07 states the §6 rule; certainty
    ranking is the §6 incomplete-meeting rule). Leftovers fall through
    as one tier.
    """
    if len(group) <= 1:
        return [list(group)]
    fmt = fmt or TeamFormat()
    secondary = _secondary(primary)
    # Certainty threshold: a missing head-to-head match can still yield
    # at most one match-win in the mini table (mp_win | max GP).
    ceiling = fmt.mp_win if primary == "MP" else _max_gp_ceiling(
        group, teams, fmt)
    mini, missing = _mini_scores(group, teams, primary)
    if all(missing[tid] == 0 for tid in group):
        tiers: List[List[int]] = []
        bucket: Dict[Fraction, List[int]] = {}
        for tid in group:
            bucket.setdefault(mini[tid], []).append(tid)
        for value in sorted(bucket, reverse=True):
            tied = bucket[value]
            if len(tied) == 1 or len(tied) == len(group):
                tiers.append(tied)
            else:
                tiers.extend(_ede_secondary_tiers(tied, teams,
                                                  secondary))
        return tiers
    remaining = list(group)
    tiers: List[List[int]] = []
    while remaining:
        mini_r, missing_r = _mini_scores(remaining, teams, primary)
        first = None
        for candidate in remaining:
            if all(mini_r[candidate]
                   > mini_r[other] + missing_r[other] * ceiling
                   for other in remaining if other != candidate):
                first = candidate
                break
        if first is None:
            tiers.append(list(remaining))
            break
        tiers.append([first])
        remaining.remove(first)
    return tiers


def _max_gp_ceiling(group: Sequence[int],
                    teams: Mapping[int, TeamRecord],
                    fmt: TeamFormat) -> float:
    """Largest known max-GP-per-match across the group (certainty cap)."""
    if fmt.max_gp_per_match is not None:
        return float(fmt.max_gp_per_match)
    known = [len(teams[tid].board_points) for tid in group
             if teams[tid].board_points]
    if not known:
        raise InvalidPlayerDataError(
            "team EDE on GP needs a board count (board_points or "
            "TeamFormat.max_gp_per_match) for the certainty threshold")
    return float(max(known))


def _ede_secondary_tiers(group: Sequence[int],
                         teams: Mapping[int, TeamRecord],
                         secondary: str) -> List[List[int]]:
    if len(group) <= 1:
        return [list(group)]
    mini, _ = _mini_scores(group, teams, secondary)
    bucket: Dict[Fraction, List[int]] = {}
    for tid in group:
        bucket.setdefault(mini[tid], []).append(tid)
    tiers = []
    for value in sorted(bucket, reverse=True):
        tied = bucket[value]
        tiers.append(tied)  # no further recursion (fall through)
    if len(tiers) == 1 and len(tiers[0]) == len(group):
        return [list(group)]
    return tiers


#: §13.3.2 chains -> knockout stages after EDE (BC scalar, TBR/BBE keys).
_CHAINS: Dict[str, Tuple[str, ...]] = {
    "EDEBT": ("BC", "TBR"),
    "EDEBB": ("BC", "BBE"),
    "EDET": ("TBR",),
    "EDEB": ("BBE",),
}


# ------------------------------------------------------------------
# Table-2 reuse on an MP/GP reference (§13 blanket rule)
# ------------------------------------------------------------------

def table2_base(team: TeamRecord, all_teams: Mapping[int, TeamRecord],
                base: str, ref: str, total_rounds: int, fmt: TeamFormat,
                primary: str = "MP", cut: int = 0,
                median: int = 0, limit_halves: int = 0) -> float:
    """Arts. 6–10 criterion on a team MP/GP reference score.

    Mapping: WIN = matches with match-win points (any contested or
    bye kind — §7.1 "with or without playing"); WON = contested
    matches only (§7.2); PS = cumulative reference score; BH = team
    Buchholz on the reference; SB = EMMSB (MP ref) / EGGSB (GP ref);
    KS = reference points vs opponents on >= 50% of the maximum
    (max = rounds × win value; ``limit_halves`` shifts by halves);
    AOB = mean of opponents' team Buchholz; FB = fore-variant BH.
    """
    if ref not in ("MP", "GP"):
        raise InvalidPlayerDataError(
            f"team reference score must be 'MP' or 'GP', got {ref!r}")
    win_value = fmt.mp_win if ref == "MP" else _max_gp(team, fmt)
    contested = [m for m in team.matches
                 if m.kind in CONTESTED_KINDS]
    if base == "WIN":
        return float(sum(1 for m in team.matches
                         if m.kind != UNPLAYED
                         and _scored(m, ref) == win_value))
    if base == "WON":
        return float(sum(1 for m in contested
                         if _scored(m, ref) == win_value))
    if base == "PS":
        # PS/Cn round-exclusion shape (mirrors the individual machine;
        # team PS accepts no /M — rejected at parse time).
        by_round: Dict[int, float] = {}
        for m in team.matches:
            by_round[m.round_number] = by_round.get(
                m.round_number, 0.0) + _scored(m, ref)
        cumulative, total = 0.0, 0.0
        excluded = 0.0
        for rnd in range(1, total_rounds + 1):
            cumulative += by_round.get(rnd, 0.0)
            total += cumulative
            if cut and rnd <= cut:
                excluded += cumulative
        return total - excluded
    if base == "BH":
        values = _ref_contribs(team, all_teams, ref, False, total_rounds,
                               fmt)
        values = _apply_cut_median(values, cut, median)
        return sum(values)
    if base == "FB":
        values = _ref_contribs(team, all_teams, ref, True, total_rounds,
                               fmt)
        values = _apply_cut_median(values, cut, median)
        return sum(values)
    if base == "SB":
        return esb(team, all_teams,
                   "EMMSB" if ref == "MP" else "EGGSB",
                   total_rounds, fmt, primary, cut)
    if base == "KS":
        threshold = total_rounds * win_value / 2 + limit_halves * 0.5
        total = 0.0
        for m in contested:
            if m.opponent_id not in all_teams:
                continue
            if _total(all_teams[m.opponent_id], ref) >= threshold:
                total += _scored(m, ref)
        return total
    if base == "AOB":
        opps = [m.opponent_id for m in contested
                if m.opponent_id in all_teams]
        if not opps:
            return 0.0
        bhs = [team_buchholz(all_teams[oid], all_teams, total_rounds,
                             fmt, ref) for oid in opps]
        return sum(bhs) / len(bhs)
    raise UnsupportedCriterionError(f"{base}:{ref}", "fide-2026")


def _ref_contribs(team: TeamRecord, all_teams: Mapping[int, TeamRecord],
                  ref: str, fore: bool, total_rounds: int,
                  fmt: TeamFormat) -> List[float]:
    opp_totals = _opponent_totals(all_teams, ref, fore, total_rounds,
                                  fmt)
    out = []
    for m in team.matches:
        if m.kind in CONTESTED_KINDS and m.opponent_id in all_teams:
            out.append(opp_totals[m.opponent_id])
        else:
            out.append(_total(team, ref))
    return out


def _apply_cut_median(values: List[float], cut: int,
                      median: int) -> List[float]:
    rest = sorted(values)
    if cut:
        rest = rest[min(cut, max(0, len(rest) - 1)):]  # keep >= 1
    if median:
        if len(rest) < 2 * median + 1:
            return rest  # documented edge mirrors individual guards
        rest = rest[median:len(rest) - median] if median else rest
    return rest


# ------------------------------------------------------------------
# Descriptor entry points (team scope)
# ------------------------------------------------------------------

def canonical_team_id(spec: ModifierSpec) -> str:
    """Criterion id for ``values`` dicts (team scope)."""
    base = spec.base.lower()
    ref = f":{spec.team_score.lower()}" if spec.team_score else ""
    suffix = ""
    if spec.cut:
        suffix += f"_c{spec.cut}"
    if spec.median:
        suffix += f"_m{spec.median}"
    if spec.limit_halves:
        sign = "+" if spec.limit_halves > 0 else ""
        suffix += f"_l{sign}{spec.limit_halves}"
    if spec.sssc_k is not None:
        suffix += f"_k{spec.sssc_k}"
    if spec.forfeits_played:
        suffix += "_p"
    if spec.fore:
        suffix += "_f"
    return f"{base}{ref}{suffix}"


_GROUP_STAGES = ("EDE", "EDEBT", "EDEBB", "EDET", "EDEB")


def _check_team_spec(spec: ModifierSpec, raw: str) -> None:
    if spec.base in ("BC", "TBR", "BBE", "MPVGP"):
        if (spec.cut or spec.median or spec.limit_halves
                or spec.sssc_k is not None or spec.forfeits_played
                or spec.fore):
            raise UnsupportedCriterionError(
                f"{raw!r} (MTB26 lists no variant for {spec.base})",
                "fide-2026")
    elif spec.base in ("EMMSB", "EMGSB", "EGMSB", "EGGSB"):
        if (spec.median or spec.limit_halves or spec.sssc_k is not None
                or spec.fore):
            raise UnsupportedCriterionError(
                f"{raw!r} (ESB accepts /C1 /C2 /P only)", "fide-2026")
        if spec.cut is not None and spec.cut > 2:
            raise UnsupportedCriterionError(
                f"{raw!r} (ESB accepts /C1 /C2 only — "
                f"FIDE names no ESB-C{spec.cut})", "fide-2026")
    elif spec.base == "SSSC":
        if spec.cut is not None and spec.cut > 2:
            raise UnsupportedCriterionError(
                f"{raw!r} (SSSC accepts /C1 /C2 only in the code "
                f"table)", "fide-2026")
        if spec.median or spec.limit_halves:
            raise UnsupportedCriterionError(
                f"{raw!r} (SSSC accepts /C /K /P /F only)", "fide-2026")
    elif spec.base in ("EDE", "EDEBT", "EDEBB", "EDET", "EDEB"):
        if (spec.cut or spec.median or spec.limit_halves
                or spec.sssc_k is not None or spec.fore):
            raise UnsupportedCriterionError(
                f"{raw!r} (EDE accepts /P only)", "fide-2026")
    elif spec.team_score is not None:
        base = spec.base
        if spec.median and base not in ("BH", "ARO", "FB"):
            raise UnsupportedCriterionError(
                f"{raw!r} (no /M combo for team {base})", "fide-2026")
        if base == "SB" and spec.median:
            raise UnsupportedCriterionError(
                f"{raw!r} (no /M combo for team SB)", "fide-2026")
        if spec.limit_halves and base != "KS":
            raise UnsupportedCriterionError(
                f"{raw!r} (only team KS accepts /L)", "fide-2026")
        if spec.sssc_k is not None:
            raise UnsupportedCriterionError(
                f"{raw!r} (only SSSC accepts /K)", "fide-2026")
        if spec.reverse:
            raise UnsupportedCriterionError(
                f"{raw!r} (team codes accept no /R)", "fide-2026")


def calculate_team(team: TeamRecord, all_teams: Mapping[int, TeamRecord],
                   descriptor: str, total_rounds: int,
                   fmt: TeamFormat | None = None,
                   primary: str = "MP") -> float:
    """Calculate one team MTB26 descriptor value (scalar scope).

    Group stages (EDE, chains) raise :class:`UnsupportedCriterionError`
    — they order groups in :func:`rank_team_standings` and have no
    per-team scalar.
    """
    fmt = fmt or TeamFormat()
    _require_primary(primary)
    _require_total_rounds(total_rounds)
    spec = parse_descriptor(descriptor)
    if not spec.is_team:
        raise UnsupportedCriterionError(
            f"{descriptor!r} (individual descriptor; use "
            f"tiebreak_core.modifiers)", "fide-2026")
    _check_team_spec(spec, descriptor)
    shared = dict(all_teams)
    if spec.base in _GROUP_STAGES:
        raise UnsupportedCriterionError(
            f"{descriptor!r} (group ranking stage; use "
            f"rank_team_standings, not calculate)", "fide-2026")
    if spec.base == "BC":
        return board_count(team, shared, total_rounds, fmt, primary)
    if spec.base == "TBR":
        return tbr_key(team)[0] if tbr_key(team) else 0.0
    if spec.base == "BBE":
        return bbe_key(team)[0] if bbe_key(team) else 0.0
    if spec.base == "MPVGP":
        return mpvgp(team, shared, total_rounds, fmt, primary)
    if spec.base in _ESB_SIDES:
        return esb(team, shared, spec.base, total_rounds, fmt, primary,
                   spec.cut or 0)
    if spec.base == "SSSC":
        if spec.cut:
            raise UnsupportedCriterionError(
                f"{descriptor!r} (SSSC/C1-C2 applies at ranking "
                f"time; scalar is uncut SSSC — use rank_team_standings)",
                "fide-2026")
        return sssc(team, shared, total_rounds, fmt, primary,
                    spec.fore, spec.sssc_k)
    if spec.team_score is not None:
        base = spec.base
        if base == "AOB" and spec.fore:
            # AOB:GP/F — mean of opponents' fore Buchholz.
            opps = [m.opponent_id for m in team.matches
                    if m.kind in CONTESTED_KINDS
                    and m.opponent_id in shared]
            if not opps:
                return 0.0
            bhs = [team_buchholz(shared[oid], shared, total_rounds,
                                 fmt, spec.team_score, True)
                   for oid in opps]
            return sum(bhs) / len(bhs)
        if base == "KS":
            return table2_base(team, shared, base, spec.team_score,
                               total_rounds, fmt, primary, 0, 0,
                               spec.limit_halves)
        return table2_base(team, shared, base, spec.team_score,
                           total_rounds, fmt, primary,
                           spec.cut or 0, spec.median or 0, 0)
    raise UnsupportedCriterionError(descriptor, "fide-2026")


def rank_team_standings(teams: Mapping[int, TeamRecord],
                        descriptors: Sequence[str], total_rounds: int,
                        fmt: TeamFormat | None = None,
                        primary: str = "MP",
                        deterministic_keys: Mapping[int, int] | None = None
                        ) -> TeamStandingsResult:
    """Rank team standings: primary first, then descriptor stages.

    Scalar stages split groups by value descending — except BC
    (ascending: lower wins, §12.1). TBR/BBE split by their full
    reapplication keys. EDE resolves groups per §13.3.1; chains
    (EDEBT/EDEBB/EDET/EDEB) continue inside exactly-two-team groups
    per §13.3.2 wording. ``values`` carries scalar descriptors only.
    """
    fmt = fmt or TeamFormat()
    _require_primary(primary)
    _require_total_rounds(total_rounds)
    specs = [parse_descriptor(d) for d in descriptors]
    shared = validate_teams(teams)
    for spec, raw in zip(specs, descriptors):
        if not spec.is_team:
            raise UnsupportedCriterionError(
                f"{raw!r} (individual descriptor; use "
                f"tiebreak_core.modifiers)", "fide-2026")
        _check_team_spec(spec, raw)
    keys = deterministic_keys or {}
    # Team id as the final tiebreak (F4, 1.2.0): fully-tied teams with
    # colliding caller keys still order deterministically.
    ordered_ids = sorted(shared,
                         key=lambda tid: (keys.get(tid, tid), tid))
    values: Dict[int, Dict[str, float]] = {tid: {} for tid in ordered_ids}
    for spec, raw in zip(specs, descriptors):
        if spec.base in _GROUP_STAGES:
            continue
        cid = canonical_team_id(spec)
        for tid in ordered_ids:
            try:
                values[tid][cid] = calculate_team(
                    shared[tid], shared, raw, total_rounds, fmt, primary)
            except UnsupportedCriterionError:
                # Ranking-only scalar facets (SSSC/Cn): fall back to
                # the stage splitter below; no per-team value stored.
                pass
    groups: List[List[int]] = _split([ordered_ids],
                                     lambda tid: -_total(shared[tid],
                                                          primary))
    for spec, raw in zip(specs, descriptors):
        if spec.base == "EDE":
            groups = [tier for g in groups
                      for tier in _ede_tiers(g, shared, primary, fmt)]
        elif spec.base in _CHAINS:
            groups = [tier for g in groups
                      for tier in _chain_tiers(g, shared, spec.base,
                                               total_rounds, fmt,
                                               primary)]
        elif spec.base == "BC":
            groups = _split(groups, lambda tid: board_count(
                shared[tid], shared, total_rounds, fmt, primary))
        elif spec.base == "TBR":
            groups = _split(groups,
                            lambda tid: _neg_tuple(tbr_key(shared[tid])))
        elif spec.base == "BBE":
            groups = _split(groups,
                            lambda tid: _neg_tuple(bbe_key(shared[tid])))
        elif spec.base == "SSSC" and spec.cut:
            groups = _split(
                groups, lambda tid: -_sssc_cut(shared[tid], shared,
                                                spec.cut or 0,
                                                total_rounds, fmt,
                                                primary, spec.fore,
                                                spec.sssc_k))
        else:
            cid = canonical_team_id(spec)
            groups = _split(
                groups, lambda tid, _c=cid: -values[tid].get(_c, 0.0))
    flat = [tid for g in groups for tid in g]
    ranked = tuple(
        TeamResult(team_id=tid, mp=shared[tid].mp, gp=shared[tid].gp,
                   values=dict(values[tid]), rank=i + 1)
        for i, tid in enumerate(flat))
    return TeamStandingsResult(teams=ranked, criteria=tuple(descriptors),
                               rules_version="fide-2026")


def _sssc_cut(team: TeamRecord, shared: Mapping[int, TeamRecord],
              cut: int, total_rounds: int, fmt: TeamFormat,
              primary: str, fore: bool, k: int | None) -> float:
    """SSSC with a cut applied to its BH dividend (code-table /C1 /C2).

    FIDE names no separate SSSC-C formula; the machine reading cuts
    the least dividend element(s) — team BH elements here carry no
    VUR provenance (no team VUR text retrieved), so plain least-cut,
    reapplied, keep-≥1. Documented PROJECT_DERIVED.
    """
    secondary = _secondary(primary)
    secondary_value = _total(team, secondary)
    values = _ref_contribs(team, shared, primary, fore, total_rounds,
                           fmt)
    rest = sorted(values)
    rest = rest[min(cut, max(0, len(rest) - 1)):]
    if primary == "MP":
        max_primary = total_rounds * fmt.mp_win
        max_secondary = _max_gp(team, fmt)
    else:
        max_primary = total_rounds * _max_gp(team, fmt)
        max_secondary = fmt.mp_win
    divisor = k if k is not None else _trunc_div(max_primary,
                                                 max_secondary)
    if divisor < 1:
        raise InvalidPlayerDataError(
            f"SSSC normaliser must be >= 1, got {divisor}")
    return secondary_value + sum(rest) / divisor


def _chain_tiers(group: Sequence[int],
                 teams: Mapping[int, TeamRecord], chain: str,
                 total_rounds: int, fmt: TeamFormat,
                 primary: str) -> List[List[int]]:
    """§13.3.2 chain inside exactly-two-team groups; else EDE only."""
    tiers = _ede_tiers(group, teams, primary, fmt)
    out: List[List[int]] = []
    for tier in tiers:
        if len(tier) != 2:
            out.append(tier)  # chains are pair-only per §13.3.2
            continue
        sub = [tier]
        for stage in _CHAINS[chain]:
            if stage == "BC":
                sub = _split(sub, lambda tid: board_count(
                    teams[tid], teams, total_rounds, fmt, primary))
            elif stage == "TBR":
                sub = _split(sub, lambda tid: _neg_tuple(
                    tbr_key(teams[tid])))
            elif stage == "BBE":
                sub = _split(sub, lambda tid: _neg_tuple(
                    bbe_key(teams[tid])))
            if len(sub) > 1:
                break  # tie broken — stop the chain
        out.extend(sub)
    return out


def _split(groups: List[List[int]], key) -> List[List[int]]:
    out: List[List[int]] = []
    for group in groups:
        bucket: Dict[float, List[int]] = {}
        for tid in group:
            bucket.setdefault(key(tid), []).append(tid)
        out.extend(bucket[k] for k in sorted(bucket))
    return out


def _neg_tuple(values: Tuple[float, ...]) -> Tuple[float, ...]:
    return tuple(-v for v in values)


__all__ = [
    "PLAYED",
    "FORFEIT_WIN",
    "FORFEIT_LOSS",
    "PAIRING_BYE",
    "UNPLAYED",
    "TEAM_KINDS",
    "TeamMatch",
    "TeamRecord",
    "TeamFormat",
    "TeamResult",
    "TeamStandingsResult",
    "validate_match",
    "validate_team",
    "validate_teams",
    "match_points",
    "game_points",
    "mpvgp",
    "team_buchholz",
    "board_count",
    "tbr_key",
    "bbe_key",
    "esb",
    "sssc",
    "table2_base",
    "canonical_team_id",
    "calculate_team",
    "rank_team_standings",
]
