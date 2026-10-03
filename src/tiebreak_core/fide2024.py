"""
FIDE-2024 calculation engine (ruleset ``fide-2024``).

Basis (PRIMARY source, retrieved in full): FIDE Council document
2024_FC2_18, "PLAY-OFF AND TIE-BREAK REGULATIONS", approved 29/07/2024,
applied 1 Aug 2024 (doc.fide.com). See docs/FIDE_SOURCES.md item 0.

Scope: individual Swiss tournaments. Out of scope (raise
``UnsupportedCriterionError``): team systems (§§11–13), rating-table
systems TPR/PTP/APRO/APPO (§§10.2–10.5, conversion tables not
retrieved), Art.16.6 local overrides. Direct Encounter (§6) is a
group-level resolution integrated into ranking (see below), not a
per-player scalar.

Key mechanics implemented:
  - Unplayed-round categories §16.2.1–§16.2.5 derived from game kinds
    (see tiebreak_core.models GAME_KINDS); 16.2.3 vs 16.2.5 decided
    positionally (a requested bye is 16.2.3 iff a later *participated*
    round — played, pairing bye or forfeit win — exists).
  - Adjusted scores §16.3 (16.2.5 rounds count as draws for opponents'
    use of your score).
  - Dummy rule §16.4 (own unplayed rounds: dummy finishing on your own
    points, result matching awarded points).
  - Cut exception §§16.5.1–16.5.2 (VUR-preferential cuts, reapplied).
  - SB-C1 definition §14.1.1.d, Median order §§14.3–14.4, ARO rounding
    §10.1 ("0.5 rounded up" — NOT banker's), Koya §9.2 (50% of maximum
    possible score; computed as specified, applied wherever requested).
  - Direct Encounter §§6.1–6.3: mini-standings over tied groups with
    forfeit exclusion (§6.1.1, Swiss scope), repeated-meeting averaging
    (§6.1.2), subset reapplication (§6.2) and Swiss conditional ranking
    (§6.3). See ADR-008.

Legacy behavior is untouched: this module never imports or calls the
legacy calculators; values here are independent implementations.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List, Mapping, Sequence, Tuple

from tiebreak_core.errors import UnsupportedCriterionError
from tiebreak_core.models import (
    FORFEIT_LOSS,
    FORFEIT_WIN,
    PAIRING_BYE,
    PLAYED,
    REQUESTED_BYE,
    PlayerResult,
    PlayerTiebreakData,
    StandingsResult,
    normalize_kind,
)

RULESET = "fide-2024"

# Categories §16.2; None = played round (no category).
CAT_PAB = "16.2.1"
CAT_FW = "16.2.2"
CAT_RB_EARLY = "16.2.3"
CAT_FL = "16.2.4"
CAT_RB_LATE = "16.2.5"

_VUR_KINDS = (REQUESTED_BYE, FORFEIT_LOSS)
# Later rounds of these kinds prove the player returned to play (§16.2.3).
_RETURN_KINDS = (PLAYED, PAIRING_BYE, FORFEIT_WIN)


@dataclass(frozen=True)
class ClassifiedRound:
    """One recorded round with its FIDE-2024 interpretation."""

    round_number: int
    kind: str
    score: float          # awarded/result points for the round
    opponent_id: int
    opponent_rating: int
    is_vur: bool          # §16.1.2: requested bye or forfeit loss
    category: str | None  # §16.2 category for unplayed rounds


def classify(player: PlayerTiebreakData) -> List[ClassifiedRound]:
    """Classify every recorded round of ``player`` (§§16.1–16.2).

    Requested byes are split positionally: 16.2.3 when a later
    *participated* round exists, else 16.2.5. Absent rounds (gaps in the
    record) are ignored for this decision — only recorded rounds carry
    availability signal (documented interpretation; FIDE assumes full
    pairing coverage in Swiss).
    """
    games = sorted(player.games, key=lambda g: g.round_number)
    kinds = [normalize_kind(g) for g in games]
    out: List[ClassifiedRound] = []
    for i, game in enumerate(games):
        kind = kinds[i]
        is_vur = kind in _VUR_KINDS
        category: str | None = None
        if kind == PAIRING_BYE:
            category = CAT_PAB
        elif kind == FORFEIT_WIN:
            category = CAT_FW
        elif kind == FORFEIT_LOSS:
            category = CAT_FL
        elif kind == REQUESTED_BYE:
            returned = any(k in _RETURN_KINDS for k in kinds[i + 1:])
            category = CAT_RB_EARLY if returned else CAT_RB_LATE
        out.append(ClassifiedRound(
            round_number=game.round_number, kind=kind,
            score=float(game.score), opponent_id=game.opponent_id,
            opponent_rating=game.opponent_rating, is_vur=is_vur,
            category=category,
        ))
    return out


def adjusted_score(rounds: List[ClassifiedRound]) -> float:
    """Score of a participant for OPPONENTS' use (§16.3).

    Categories 16.2.1–16.2.4 count awarded points; 16.2.5 counts as a
    draw (0.5). Played rounds count actual scores.
    """
    total = 0.0
    for r in rounds:
        if r.category == CAT_RB_LATE:
            total += 0.5
        else:
            total += r.score
    return total


@dataclass(frozen=True)
class _Contribution:
    """One summable tie-break element with VUR provenance (§16.5)."""

    value: float
    from_vur: bool


def _buchholz_contribs(own_points: float, own_rounds: List[ClassifiedRound],
                       adj: Mapping[int, float]) -> List[_Contribution]:
    """Buchholz elements: adj(opp) for played, own points (dummy §16.4)."""
    out: List[_Contribution] = []
    for r in own_rounds:
        if r.kind == PLAYED:
            out.append(_Contribution(adj[r.opponent_id], False))
        else:
            out.append(_Contribution(own_points, r.is_vur))
    return out


def _sb_contribs(own_points: float, own_rounds: List[ClassifiedRound],
                 adj: Mapping[int, float]) -> List[_Contribution]:
    """SB elements: adj(opp) × score; dummy §16.4 for unplayed rounds."""
    out: List[_Contribution] = []
    for r in own_rounds:
        if r.kind == PLAYED:
            out.append(_Contribution(adj[r.opponent_id] * r.score, False))
        else:
            out.append(_Contribution(own_points * r.score, r.is_vur))
    return out


def _cut_least_exception(values: List[_Contribution]) -> float:
    """Cut one least-significant value with the §16.5.1 VUR exception.

    With VUR contributions present, cut the lowest VUR contribution
    (literal rule; it is never lower than the overall minimum). Without
    VURs, cut the plain minimum. Returns the cut value.
    """
    vur = [c.value for c in values if c.from_vur]
    if vur:
        return min(vur)
    return min(c.value for c in values)


def _apply_cuts_least(values: List[_Contribution], n: int) -> List[_Contribution]:
    """Remove ``n`` least-significant values, reapplying §16.5.1 (§16.5.2).

    Never cuts the last remaining element (mirrors the legacy edge
    guard). When the cut is VUR-driven, a VUR element is removed.
    """
    remaining = list(values)
    for _ in range(min(n, max(0, len(remaining) - 1))):
        cut = _cut_least_exception(remaining)
        vur_vals = [c.value for c in remaining if c.from_vur]
        if vur_vals and cut == min(vur_vals):
            remaining.remove(next(
                c for c in remaining if c.value == cut and c.from_vur))
        else:
            remaining.remove(next(c for c in remaining if c.value == cut))
    return remaining


def _remove_max(values: List[_Contribution]) -> List[_Contribution]:
    top = max(c.value for c in values)
    remaining = list(values)
    remaining.remove(next(c for c in remaining if c.value == top))
    return remaining


def _require_context(players: Mapping[int, PlayerTiebreakData],
                     total_rounds: int) -> Dict[int, List[ClassifiedRound]]:
    if (isinstance(total_rounds, bool) or not isinstance(total_rounds, int)
            or total_rounds < 1):
        from tiebreak_core.errors import InvalidPlayerDataError
        raise InvalidPlayerDataError(
            f"fide-2024 requires total_rounds (tournament rounds) >= 1, "
            f"got {total_rounds!r}")
    return {pid: classify(p) for pid, p in players.items()}


def _adj_table(players: Mapping[int, PlayerTiebreakData],
               ctx: Mapping[int, List[ClassifiedRound]]) -> Dict[int, float]:
    return {pid: adjusted_score(ctx[pid]) for pid in players}


def validate_inputs(players: Mapping[int, PlayerTiebreakData],
                    total_rounds: int) -> None:
    """fide-2024 input gate (called by the strict path).

    Beyond generic validation: uncategorized unplayed rounds (the legacy
    ``-1`` sentinel without an explicit game kind) are REJECTED — FIDE
    Article 16 assigns them different arithmetic per category, so
    computing would require inventing a category. Callers must
    categorize first (see GAME_KINDS + ADR-006).
    """
    from tiebreak_core.errors import InvalidGameRecordError
    from tiebreak_core.models import UNPLAYED
    _require_context(players, total_rounds)
    for pid, pdata in players.items():
        for i, game in enumerate(pdata.games):
            if (game.opponent_id == -1
                    and normalize_kind(game) == UNPLAYED):
                raise InvalidGameRecordError(
                    f"player {pid} game[{i}]: uncategorized unplayed round "
                    f"(opponent_id=-1 without explicit kind) cannot be "
                    f"computed under fide-2024; categorize it with one of "
                    f"pairing_bye/forfeit_win/forfeit_loss/requested_bye/"
                    f"absent first")
        recorded = sum(float(g.score) for g in pdata.games)
        # Empty records are context-only (opponent scores without their
        # histories): nothing to reconstruct, points taken as given.
        # Non-empty records must be coherent — PS gap-filling and the
        # §16.4 dummy rule build on per-round scores.
        if pdata.games and not math.isclose(recorded, pdata.points,
                                            abs_tol=1e-9):
            from tiebreak_core.errors import InvalidPlayerDataError
            raise InvalidPlayerDataError(
                f"player {pid}: points {pdata.points} != sum of recorded "
                f"round scores {recorded}; fide-2024 reconstructions "
                f"(progressive, dummy rule) require coherent inputs")


# ------------------------------------------------------------------
# Individual calculators: (player, all_players, total_rounds) -> float
# ------------------------------------------------------------------

def buchholz(player: PlayerTiebreakData,
             all_players: Mapping[int, PlayerTiebreakData],
             total_rounds: int) -> float:
    """§8.1 with §§16.3–16.4. Exact sum (no rounding)."""
    ctx = _require_context(all_players, total_rounds)
    adj = _adj_table(all_players, ctx)
    return sum(c.value for c in _buchholz_contribs(
        player.points, ctx[player.player_id], adj))


def buchholz_cut1(player: PlayerTiebreakData,
                  all_players: Mapping[int, PlayerTiebreakData],
                  total_rounds: int) -> float:
    """BH-C1 §14.1.1.a with §16.5.1. Single score kept uncut (edge)."""
    ctx = _require_context(all_players, total_rounds)
    adj = _adj_table(all_players, ctx)
    contribs = _buchholz_contribs(player.points, ctx[player.player_id], adj)
    if len(contribs) < 2:
        return sum(c.value for c in contribs)
    cut = _cut_least_exception(contribs)
    return sum(c.value for c in contribs) - cut


def buchholz_cut2(player: PlayerTiebreakData,
                  all_players: Mapping[int, PlayerTiebreakData],
                  total_rounds: int) -> float:
    """BH-C2 §14.2 with §16.5.2 (exception reapplied). Keeps ≥1 element."""
    ctx = _require_context(all_players, total_rounds)
    adj = _adj_table(all_players, ctx)
    contribs = _buchholz_contribs(player.points, ctx[player.player_id], adj)
    if len(contribs) < 2:
        return sum(c.value for c in contribs)
    return sum(c.value for c in _apply_cuts_least(contribs, 2))


def median_buchholz(player: PlayerTiebreakData,
                    all_players: Mapping[int, PlayerTiebreakData],
                    total_rounds: int) -> float:
    """BH-M1 §14.3 (least then most). <3 elements → full BH (edge)."""
    ctx = _require_context(all_players, total_rounds)
    adj = _adj_table(all_players, ctx)
    contribs = _buchholz_contribs(player.points, ctx[player.player_id], adj)
    if len(contribs) < 3:
        return sum(c.value for c in contribs)
    rest = _apply_cuts_least(contribs, 1)
    return sum(c.value for c in _remove_max(rest))


def median_buchholz_2(player: PlayerTiebreakData,
                      all_players: Mapping[int, PlayerTiebreakData],
                      total_rounds: int) -> float:
    """BH-M2 §14.4 with §16.5.2. <5 elements → full BH (edge)."""
    ctx = _require_context(all_players, total_rounds)
    adj = _adj_table(all_players, ctx)
    contribs = _buchholz_contribs(player.points, ctx[player.player_id], adj)
    if len(contribs) < 5:
        return sum(c.value for c in contribs)
    rest = _apply_cuts_least(contribs, 2)
    rest = _remove_max(rest)
    return sum(c.value for c in _remove_max(rest))


def sonneborn_berger(player: PlayerTiebreakData,
                     all_players: Mapping[int, PlayerTiebreakData],
                     total_rounds: int) -> float:
    """§9.1 with §§16.3–16.4. Exact sum (no rounding)."""
    ctx = _require_context(all_players, total_rounds)
    adj = _adj_table(all_players, ctx)
    return sum(c.value for c in _sb_contribs(
        player.points, ctx[player.player_id], adj))


def sonneborn_berger_cut1(player: PlayerTiebreakData,
                          all_players: Mapping[int, PlayerTiebreakData],
                          total_rounds: int) -> float:
    """SB-C1 §14.1.1.d with §16.5.1 (cut higher of lowest-VUR/lowest)."""
    ctx = _require_context(all_players, total_rounds)
    adj = _adj_table(all_players, ctx)
    contribs = _sb_contribs(player.points, ctx[player.player_id], adj)
    if len(contribs) < 2:
        return sum(c.value for c in contribs)
    vur = [c.value for c in contribs if c.from_vur]
    least = min(c.value for c in contribs)
    cut = max(min(vur), least) if vur else least
    remaining = list(contribs)
    remaining.remove(next(c for c in remaining if c.value == cut))
    return sum(c.value for c in remaining)


def progressive(player: PlayerTiebreakData,
                all_players: Mapping[int, PlayerTiebreakData],
                total_rounds: int) -> float:
    """§7.5 over all tournament rounds (gap-filled; absent carries)."""
    ctx = _require_context(all_players, total_rounds)
    by_round: Dict[int, float] = {}
    for r in ctx[player.player_id]:
        by_round[r.round_number] = by_round.get(r.round_number, 0.0) + r.score
    cumulative, total = 0.0, 0.0
    for rnd in range(1, total_rounds + 1):
        cumulative += by_round.get(rnd, 0.0)
        total += cumulative
    return total


def progressive_cut1(player: PlayerTiebreakData,
                     all_players: Mapping[int, PlayerTiebreakData],
                     total_rounds: int) -> float:
    """PS-C1 §14.1.1.c: exclude the score achieved after the first round."""
    ctx = _require_context(all_players, total_rounds)
    by_round: Dict[int, float] = {}
    for r in ctx[player.player_id]:
        by_round[r.round_number] = by_round.get(r.round_number, 0.0) + r.score
    cumulative, total, first = 0.0, 0.0, 0.0
    for rnd in range(1, total_rounds + 1):
        cumulative += by_round.get(rnd, 0.0)
        if rnd == 1:
            first = cumulative
        total += cumulative
    return total - first


def _otb_opponents(player: PlayerTiebreakData,
                   all_players: Mapping[int, PlayerTiebreakData],
                   total_rounds: int) -> List[PlayerTiebreakData]:
    ctx = _require_context(all_players, total_rounds)
    opps = []
    for r in ctx[player.player_id]:
        if r.kind == PLAYED and r.opponent_id in all_players:
            opps.append(all_players[r.opponent_id])
    return opps


def wins(player: PlayerTiebreakData,
         all_players: Mapping[int, PlayerTiebreakData],
         total_rounds: int) -> float:
    """WIN §7.1: rounds with win-points, with or without playing."""
    ctx = _require_context(all_players, total_rounds)
    return float(sum(1 for r in ctx[player.player_id] if r.score == 1.0))


def won(player: PlayerTiebreakData,
        all_players: Mapping[int, PlayerTiebreakData],
        total_rounds: int) -> float:
    """WON §7.2: games won over the board."""
    ctx = _require_context(all_players, total_rounds)
    return float(sum(1 for r in ctx[player.player_id]
                     if r.kind == PLAYED and r.score == 1.0))


def games_black(player: PlayerTiebreakData,
                all_players: Mapping[int, PlayerTiebreakData],
                total_rounds: int) -> float:
    """BPG §7.3: games played over the board with black."""
    _require_context(all_players, total_rounds)
    return float(sum(1 for g in player.games
                     if normalize_kind(g) == PLAYED and g.color == "black"))


def wins_black(player: PlayerTiebreakData,
               all_players: Mapping[int, PlayerTiebreakData],
               total_rounds: int) -> float:
    """BWG §7.4: games won over the board with black."""
    _require_context(all_players, total_rounds)
    return float(sum(1 for g in player.games
                     if normalize_kind(g) == PLAYED and g.color == "black"
                     and g.score == 1.0))


def rounds_played_elected(player: PlayerTiebreakData,
                          all_players: Mapping[int, PlayerTiebreakData],
                          total_rounds: int) -> float:
    """REP §7.6: recorded non-absent rounds minus half/zero-byes and
    forfeit losses."""
    from tiebreak_core.models import ABSENT
    ctx = _require_context(all_players, total_rounds)
    rounds = [r for r in ctx[player.player_id] if r.kind != ABSENT]
    excluded = sum(1 for r in rounds if r.is_vur)
    return float(len(rounds) - excluded)


def _fide_round_half_up(value: float) -> int:
    """Round to nearest whole number, 0.5 up (§10.1 etc.)."""
    return int(math.floor(value + 0.5))


def average_rating_opponents(player: PlayerTiebreakData,
                             all_players: Mapping[int, PlayerTiebreakData],
                             total_rounds: int) -> float:
    """ARO §10.1: average rating of OTB opponents, 0.5 rounded up.

    Opponents without a positive rating are excluded (callers must drop
    the criterion when unrated players are present without published
    handling rules — §10 intro). Empty set → 0.0 (documented edge).
    """
    opps = [o for o in _otb_opponents(player, all_players, total_rounds)
            if o.rating > 0]
    if not opps:
        return 0.0
    return float(_fide_round_half_up(sum(o.rating for o in opps) / len(opps)))


def aro_cut1(player: PlayerTiebreakData,
             all_players: Mapping[int, PlayerTiebreakData],
             total_rounds: int) -> float:
    """ARO-C1 §14.1.1.b: exclude the lowest opponent rating.

    VUR rounds contribute no opponent rating, so the §16.5 exception has
    no element to prefer; the plain lowest rating is cut. Fewer than 2
    rated OTB opponents → uncut ARO (documented edge).
    """
    opps = sorted(
        (o for o in _otb_opponents(player, all_players, total_rounds)
         if o.rating > 0),
        key=lambda o: o.rating)
    if len(opps) < 2:
        return average_rating_opponents(player, all_players, total_rounds)
    rest = opps[1:]
    return float(_fide_round_half_up(
        sum(o.rating for o in rest) / len(rest)))


def average_opponents_buchholz(player: PlayerTiebreakData,
                               all_players: Mapping[int, PlayerTiebreakData],
                               total_rounds: int) -> float:
    """AOB §8.2: average of OTB opponents' (fide-2024) Buchholz.

    Rounded to 1 decimal (documented presentation choice; FIDE states no
    rounding for AOB). Empty set → 0.0.
    """
    ctx = _require_context(all_players, total_rounds)
    adj = _adj_table(all_players, ctx)
    opp_ids = [r.opponent_id for r in ctx[player.player_id]
               if r.kind == PLAYED and r.opponent_id in all_players]
    if not opp_ids:
        return 0.0
    bhs = [sum(c.value for c in _buchholz_contribs(
        all_players[oid].points, ctx[oid], adj)) for oid in opp_ids]
    return round(sum(bhs) / len(bhs), 1)


def fore_buchholz(player: PlayerTiebreakData,
                  all_players: Mapping[int, PlayerTiebreakData],
                  total_rounds: int) -> float:
    """FB §8.3: Buchholz with final-round *paired* games as draws.

    Unpaired final rounds (byes) keep their awarded points; Art.16
    applies on top, with the dummy rule using FB-adjusted own points.
    """
    ctx = _require_context(all_players, total_rounds)
    fb_points: Dict[int, float] = {}
    for pid, rounds in ctx.items():
        pts = 0.0
        for r in rounds:
            if r.kind == PLAYED and r.round_number == total_rounds:
                pts += 0.5
            elif r.category == CAT_RB_LATE:
                pts += r.score  # unpaired: awarded stands (16.3 on top)
            else:
                pts += r.score
        fb_points[pid] = pts

    def fb_adj(pid: int) -> float:
        total = 0.0
        for r in ctx[pid]:
            if r.category == CAT_RB_LATE:
                total += 0.5
            elif r.kind == PLAYED and r.round_number == total_rounds:
                total += 0.5
            else:
                total += r.score
        return total

    adj = {pid: fb_adj(pid) for pid in all_players}
    total = 0.0
    for r in ctx[player.player_id]:
        if r.kind == PLAYED:
            total += adj[r.opponent_id]
        else:
            total += fb_points[player.player_id]
    return total


def koya(player: PlayerTiebreakData,
         all_players: Mapping[int, PlayerTiebreakData],
         total_rounds: int) -> float:
    """KS §9.2: points vs opponents on ≥50% of the maximum possible.

    Maximum possible = total tournament rounds (1 pt/round). Koya is not
    Art.16-managed, so opponent qualification uses raw final points and
    all real-opponent games count (cf. §15.2 spirit). Documented as
    applied wherever requested (FIDE scopes Koya to round robin).
    """
    ctx = _require_context(all_players, total_rounds)
    threshold = total_rounds / 2
    total = 0.0
    for g in player.games:
        if normalize_kind(g) != PLAYED or g.opponent_id not in all_players:
            continue
        if all_players[g.opponent_id].points >= threshold:
            total += g.score
    return total


def _rated_otb_games(player: PlayerTiebreakData,
                     all_players: Mapping[int, PlayerTiebreakData]
                     ) -> List[Tuple[float, int]]:
    """(score, opponent rating) for rated over-the-board games."""
    out: List[Tuple[float, int]] = []
    for game in player.games:
        if normalize_kind(game) != PLAYED:
            continue
        opp = all_players.get(game.opponent_id)
        if opp is None or opp.rating <= 0:
            continue
        out.append((float(game.score), opp.rating))
    return out


def _dp_for_fraction(points: float, games: int) -> int:
    """Rating difference for a fractional score (§8.1a table).

    The fraction is rounded half-up to hundredths first (documented
    interpretation — FIDE specifies the table granularity, not the
    rounding direction; half-up matches §10.1's "0.5 rounded up").
    """
    if games <= 0:
        return 0
    hundredths = int(math.floor(points / games * 100 + 0.5))
    hundredths = min(100, max(0, hundredths))
    return _DP_BY_HUNDREDTH[hundredths]


def _pd_for_rating(own: int, opp: int) -> float:
    """Scoring probability for ``own`` vs ``opp`` (§8.1b table).

    Full rating scale (no ±400 cut — explicit in §10.3, applied
    throughout the rating family here).
    """
    diff = own - opp
    magnitude = abs(diff)
    for lo, hi, high, low in _PD_RANGES:
        if lo <= magnitude <= hi:
            return high if diff >= 0 else low
    return 1.0 if diff >= 0 else 0.0  # unreachable; defensive


def tournament_performance(player: PlayerTiebreakData,
                           all_players: Mapping[int, PlayerTiebreakData],
                           total_rounds: int) -> float:
    """TPR §10.2: rounded ARO + table rating difference.

    ARO here is the §10.1 quantity (0.5 rounded up); the fraction is
    points in rated OTB games over their count. No rated OTB games →
    0.0 (documented edge, consistent with ARO).
    """
    _require_context(all_players, total_rounds)
    games = _rated_otb_games(player, all_players)
    if not games:
        return 0.0
    aro = _fide_round_half_up(sum(r for _, r in games) / len(games))
    points = sum(s for s, _ in games)
    return float(aro + _dp_for_fraction(points, len(games)))


def perfect_performance(player: PlayerTiebreakData,
                        all_players: Mapping[int, PlayerTiebreakData],
                        total_rounds: int) -> float:
    """PTP §10.3: lowest rating with expected score ≥ tournament score.

    Expected score sums §8.1b probabilities over rated OTB opponents;
    the target is points scored in those games (documented
    interpretation — FIDE is silent on unplayed handling for PTP, which
    is not Art.16-managed; comparing OTB points against OTB-based
    expectation is the coherent reading). Zero target → 800 below the
    lowest rated opponent (per spec). No rated OTB games → 0.0.
    Found by binary search (expected score is monotone in rating).
    """
    _require_context(all_players, total_rounds)
    games = _rated_otb_games(player, all_players)
    if not games:
        return 0.0
    target = sum(s for s, _ in games)
    lowest = min(r for _, r in games)
    if target <= 0:
        return float(lowest - 800)

    def expected(rating: int) -> float:
        return sum(_pd_for_rating(rating, opp) for _, opp in games)

    lo = lowest - 800  # expected ≈ 0 < target (target > 0)
    hi = max(r for _, r in games) + 800  # expected = n ≥ target
    while lo < hi:
        mid = (lo + hi) // 2
        if expected(mid) >= target:
            hi = mid
        else:
            lo = mid + 1
    return float(lo)


def _average_opponent_metric(
        player: PlayerTiebreakData,
        all_players: Mapping[int, PlayerTiebreakData],
        total_rounds: int, metric) -> float:
    """Mean of ``metric`` over OTB opponents (§§10.4–10.5 shape)."""
    ctx = _require_context(all_players, total_rounds)
    opps = [r.opponent_id for r in ctx[player.player_id]
            if r.kind == PLAYED and r.opponent_id in all_players]
    if not opps:
        return 0.0
    vals = [metric(all_players[oid], all_players, total_rounds)
            for oid in opps]
    return float(_fide_round_half_up(sum(vals) / len(vals)))


def apro(player: PlayerTiebreakData,
         all_players: Mapping[int, PlayerTiebreakData],
         total_rounds: int) -> float:
    """APRO §10.4: average of OTB opponents' TPR, 0.5 rounded up."""
    return _average_opponent_metric(player, all_players, total_rounds,
                                    tournament_performance)


def appo(player: PlayerTiebreakData,
         all_players: Mapping[int, PlayerTiebreakData],
         total_rounds: int) -> float:
    """APPO §10.5: average of OTB opponents' PTP, 0.5 rounded up."""
    return _average_opponent_metric(player, all_players, total_rounds,
                                    perfect_performance)


# ------------------------------------------------------------------
# Official FIDE rating tables (embedded verbatim data).
#
# _DP_BY_HUNDREDTH: fractional score p (as integer hundredths 0..100)
#   -> rating difference dp. Source: FIDE Rating Regulations §8.1a
#   (table of conversion from fractional score into rating differences;
#   extracted from the official 2022 PDF, "FIDE Rating Regulations
#   effective from 1 January 2022"; table stable across editions —
#   identical values confirmed in the 2024 rapid/blitz excerpts).
# _PD_RANGES: (lo, hi, PD_H, PD_L) rating-difference bands. Source:
#   same document, §8.1b (conversion of difference in rating into
#   scoring probability). Full 0..735 coverage verified on extraction.
# ------------------------------------------------------------------

_DP_BY_HUNDREDTH: Dict[int, int] = {
    0: -800, 1: -677, 2: -589, 3: -538,
    4: -501, 5: -470, 6: -444, 7: -422,
    8: -401, 9: -383, 10: -366, 11: -351,
    12: -336, 13: -322, 14: -309, 15: -296,
    16: -284, 17: -273, 18: -262, 19: -251,
    20: -240, 21: -230, 22: -220, 23: -211,
    24: -202, 25: -193, 26: -184, 27: -175,
    28: -166, 29: -158, 30: -149, 31: -141,
    32: -133, 33: -125, 34: -117, 35: -110,
    36: -102, 37: -95, 38: -87, 39: -80,
    40: -72, 41: -65, 42: -57, 43: -50,
    44: -43, 45: -36, 46: -29, 47: -21,
    48: -14, 49: -7, 50: 0, 51: 7,
    52: 14, 53: 21, 54: 29, 55: 36,
    56: 43, 57: 50, 58: 57, 59: 65,
    60: 72, 61: 80, 62: 87, 63: 95,
    64: 102, 65: 110, 66: 117, 67: 125,
    68: 133, 69: 141, 70: 149, 71: 158,
    72: 166, 73: 175, 74: 184, 75: 193,
    76: 202, 77: 211, 78: 220, 79: 230,
    80: 240, 81: 251, 82: 262, 83: 273,
    84: 284, 85: 296, 86: 309, 87: 322,
    88: 336, 89: 351, 90: 366, 91: 383,
    92: 401, 93: 422, 94: 444, 95: 470,
    96: 501, 97: 538, 98: 589, 99: 677,
    100: 800,
}

_PD_RANGES: Tuple[Tuple[int, int, float, float], ...] = (
    (0, 3, 0.5, 0.5),
    (4, 10, 0.51, 0.49),
    (11, 17, 0.52, 0.48),
    (18, 25, 0.53, 0.47),
    (26, 32, 0.54, 0.46),
    (33, 39, 0.55, 0.45),
    (40, 46, 0.56, 0.44),
    (47, 53, 0.57, 0.43),
    (54, 61, 0.58, 0.42),
    (62, 68, 0.59, 0.41),
    (69, 76, 0.6, 0.4),
    (77, 83, 0.61, 0.39),
    (84, 91, 0.62, 0.38),
    (92, 98, 0.63, 0.37),
    (99, 106, 0.64, 0.36),
    (107, 113, 0.65, 0.35),
    (114, 121, 0.66, 0.34),
    (122, 129, 0.67, 0.33),
    (130, 137, 0.68, 0.32),
    (138, 145, 0.69, 0.31),
    (146, 153, 0.7, 0.3),
    (154, 162, 0.71, 0.29),
    (163, 170, 0.72, 0.28),
    (171, 179, 0.73, 0.27),
    (180, 188, 0.74, 0.26),
    (189, 197, 0.75, 0.25),
    (198, 206, 0.76, 0.24),
    (207, 215, 0.77, 0.23),
    (216, 225, 0.78, 0.22),
    (226, 235, 0.79, 0.21),
    (236, 245, 0.8, 0.2),
    (246, 256, 0.81, 0.19),
    (257, 267, 0.82, 0.18),
    (268, 278, 0.83, 0.17),
    (279, 290, 0.84, 0.16),
    (291, 302, 0.85, 0.15),
    (303, 315, 0.86, 0.14),
    (316, 328, 0.87, 0.13),
    (329, 344, 0.88, 0.12),
    (345, 357, 0.89, 0.11),
    (358, 374, 0.9, 0.1),
    (375, 391, 0.91, 0.09),
    (392, 411, 0.92, 0.08),
    (412, 432, 0.93, 0.07),
    (433, 456, 0.94, 0.06),
    (457, 484, 0.95, 0.05),
    (485, 517, 0.96, 0.04),
    (518, 559, 0.97, 0.03),
    (560, 619, 0.98, 0.02),
    (620, 735, 0.99, 0.01),
    (736, 10**9, 1.0, 0.0),
)

# ------------------------------------------------------------------
# Registry, dispatcher, ranking
# ------------------------------------------------------------------

FIDE2024_IDS: Tuple[str, ...] = (
    "buchholz",
    "buchholz_cut1",
    "buchholz_cut2",
    "median_buchholz",
    "median_buchholz_2",
    "sonneborn_berger",
    "sonneborn_berger_cut1",
    "progressive",
    "progressive_cut1",
    "wins",
    "won",
    "games_black",
    "wins_black",
    "rounds_elected",
    "aro",
    "aro_cut1",
    "aob",
    "fore_buchholz",
    "koya",
    "tpr",
    "ptp",
    "apro",
    "appo",
)

FIDE2024_REGISTRY = {
    "buchholz": buchholz,
    "buchholz_cut1": buchholz_cut1,
    "buchholz_cut2": buchholz_cut2,
    "median_buchholz": median_buchholz,
    "median_buchholz_2": median_buchholz_2,
    "sonneborn_berger": sonneborn_berger,
    "sonneborn_berger_cut1": sonneborn_berger_cut1,
    "progressive": progressive,
    "progressive_cut1": progressive_cut1,
    "wins": wins,
    "won": won,
    "games_black": games_black,
    "wins_black": wins_black,
    "rounds_elected": rounds_played_elected,
    "aro": average_rating_opponents,
    "aro_cut1": aro_cut1,
    "aob": average_opponents_buchholz,
    "fore_buchholz": fore_buchholz,
    "koya": koya,
    "tpr": tournament_performance,
    "ptp": perfect_performance,
    "apro": apro,
    "appo": appo,
}

#: Legacy ids with *different* fide-2024 semantics (same id, ruleset
#: namespaces the meaning — documented in docs/TIEBREAK_RULES.md).
REDEFINED_IDS: Tuple[str, ...] = (
    "koya", "aro", "wins", "wins_black", "games_black", "progressive",
)

#: Group-level (non-scalar) ranking stages.
GROUP_CRITERIA: Tuple[str, ...] = ("direct_encounter",)


def is_supported_criterion(criterion: str) -> bool:
    """True iff ``criterion`` is implemented under fide-2024."""
    return criterion in FIDE2024_REGISTRY


def require_supported(criterion: str) -> None:
    """Raise for ids unknown or unimplemented under fide-2024."""
    from tiebreak_core.registry import is_known
    if not is_known(criterion) and criterion not in FIDE2024_REGISTRY:
        from tiebreak_core.errors import UnknownCriterionError
        raise UnknownCriterionError(criterion)
    if criterion not in FIDE2024_REGISTRY:
        from tiebreak_core.errors import UnsupportedCriterionError
        raise UnsupportedCriterionError(criterion, RULESET)


def calculate(player: PlayerTiebreakData,
              all_players: Mapping[int, PlayerTiebreakData],
              criterion: str, total_rounds: int) -> float:
    """Single fide-2024 calculation (validated upstream by strict)."""
    require_supported(criterion)
    return FIDE2024_REGISTRY[criterion](player, dict(all_players),
                                        total_rounds)


def calculate_all(player: PlayerTiebreakData,
                  all_players: Mapping[int, PlayerTiebreakData],
                  criteria: Sequence[str], total_rounds: int) -> Dict[str, float]:
    """Multi-criterion fide-2024 calculation."""
    return {c: calculate(player, all_players, c, total_rounds)
            for c in criteria}


def rank_standings(players: Mapping[int, PlayerTiebreakData],
                   criteria: Sequence[str], total_rounds: int,
                   deterministic_keys: Mapping[int, int] | None = None,
                   ) -> StandingsResult:
    """fide-2024 values + staged ordering (points, then criteria in order).

    Scalar criteria split groups by value (descending); the group-level
    ``direct_encounter`` resolves tied groups per §§6.1–6.3. Groups that
    no stage can split fall back to ``deterministic_keys`` (pre-sorted,
    so every sort stage is stable). ``values`` carries scalar criteria
    only — group-level criteria have no per-player scalar (documented).
    """
    _require_context(players, total_rounds)
    check_ranking_criteria(criteria)
    keys = deterministic_keys or {}
    ordered_ids = sorted(players,
                         key=lambda pid: keys.get(pid, pid))
    scalar = [c for c in criteria if c in FIDE2024_REGISTRY]
    shared = dict(players)
    values: Dict[int, Dict[str, float]] = {
        pid: {c: FIDE2024_REGISTRY[c](shared[pid], shared, total_rounds)
              for c in scalar}
        for pid in ordered_ids
    }
    groups: List[List[int]] = _split_by(
        [ordered_ids], lambda pid: -(shared[pid].points or 0.0))
    for criterion in criteria:
        if criterion in GROUP_CRITERIA:
            groups = [tier for g in groups for tier in _de_tiers(g, shared)]
        else:
            groups = _split_by(
                groups, lambda pid: -values[pid][criterion])
    flat = [pid for g in groups for pid in g]
    ranked = tuple(
        PlayerResult(player_id=pid, points=shared[pid].points or 0.0,
                     values=dict(values[pid]), rank=i + 1)
        for i, pid in enumerate(flat))
    return StandingsResult(players=ranked, criteria=tuple(criteria),
                           rules_version=RULESET)


def _split_by(groups: List[List[int]],
              key) -> List[List[int]]:
    """Split each group into strict subgroups by key (order preserved)."""
    out: List[List[int]] = []
    for group in groups:
        bucket: Dict[float, List[int]] = {}
        for pid in group:
            bucket.setdefault(key(pid), []).append(pid)
        out.extend(bucket[k] for k in sorted(bucket))
    return out


def check_ranking_criteria(criteria: Sequence[str]) -> None:
    """Validate a ranking criteria sequence (scalars + group stages)."""
    for criterion in criteria:
        if criterion in GROUP_CRITERIA:
            continue
        require_supported(criterion)


# ------------------------------------------------------------------
# Direct Encounter §§6.1–6.3 (group-level; Swiss scope)
# ------------------------------------------------------------------


def _mini_table(group: Sequence[int],
                players: Mapping[int, PlayerTiebreakData]
                ) -> Tuple[Dict[int, Fraction], Dict[int, int]]:
    """Mini-standings over a tied group (§6.1).

    Only games between group members with kind ``played`` count;
    forfeit results are excluded (Swiss scope, §6.1.1). Pairs meeting
    more than once contribute each side's average (§6.1.2). Returns
    (mini-scores, unplayed-pair counts). A pair counts as unplayed when
    NO game record exists between them in either direction
    (documented interpretation — excluded forfeit pairs are fixed
    exclusions, not variable outcomes).
    """
    gset = set(group)
    scores: Dict[int, Fraction] = {pid: Fraction(0) for pid in group}
    missing: Dict[int, int] = {pid: 0 for pid in group}
    done = set()
    for pid in group:
        own = [g for g in players[pid].games
               if g.opponent_id in gset and g.opponent_id != pid
               and normalize_kind(g) == PLAYED]
        by_opp: Dict[int, List[float]] = {}
        for game in own:
            by_opp.setdefault(game.opponent_id, []).append(float(game.score))
        for opp, scs in by_opp.items():
            pair = (min(pid, opp), max(pid, opp))
            if pair in done:
                continue
            done.add(pair)
            scores[pid] += sum(Fraction(s) for s in scs) / len(scs)
    for idx, first in enumerate(group):
        for second in group[idx + 1:]:
            met = any(g.opponent_id == second for g in players[first].games) \
                or any(g.opponent_id == first for g in players[second].games)
            if not met:
                missing[first] += 1
                missing[second] += 1
    return scores, missing


def _de_tiers(group: Sequence[int],
              players: Mapping[int, PlayerTiebreakData]) -> List[List[int]]:
    """Resolve one tied group per §6 into ordered tiers (best first).

    All-met groups follow §6.2 (mini-table order, recursive reapplication
    to tied subsets). Otherwise §6.3 certainty ranking applies iteratively;
    whatever remains unresolvable is returned as one tier (falls through
    to subsequent criteria).
    """
    if len(group) <= 1:
        return [list(group)]
    scores, missing = _mini_table(group, players)
    if all(missing[pid] == 0 for pid in group):
        tiers: List[List[int]] = []
        bucket: Dict[Fraction, List[int]] = {}
        for pid in group:
            bucket.setdefault(scores[pid], []).append(pid)
        for score in sorted(bucket, reverse=True):
            tied = bucket[score]
            if len(tied) == 1 or len(tied) == len(group):
                # Single player, or no progress possible (e.g. empty
                # mini-table after forfeit exclusion): one tier, so the
                # ranking falls through to subsequent criteria.
                tiers.append(tied)
            else:
                tiers.extend(_de_tiers(tied, players))  # §6.2 reapply
        return tiers
    remaining = list(group)
    tiers = []
    while remaining:
        scores_r, missing_r = _mini_table(remaining, players)
        first = None
        for candidate in remaining:
            if all(scores_r[candidate]
                   > scores_r[other] + missing_r[other]
                   for other in remaining if other != candidate):
                first = candidate
                break  # at most one can satisfy (sums are fixed)
        if first is None:
            tiers.append(list(remaining))
            break
        tiers.append([first])
        remaining.remove(first)
    return tiers
