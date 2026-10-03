"""
FIDE-2024 calculation engine (ruleset ``fide-2024``).

Basis (PRIMARY source, retrieved in full): FIDE Council document
2024_FC2_18, "PLAY-OFF AND TIE-BREAK REGULATIONS", approved 29/07/2024,
applied 1 Aug 2024 (doc.fide.com). See docs/FIDE_SOURCES.md item 0.

Scope: individual Swiss tournaments. Out of scope (raise
``UnsupportedCriterionError``): team systems (§§11–13), rating-table
systems TPR/PTP/APRO/APPO (§§10.2–10.5, conversion tables not
retrieved), Direct Encounter (§6 — needs the group-context ranking
architecture, roadmap Phase 3), Art.16.6 local overrides.

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

Legacy behavior is untouched: this module never imports or calls the
legacy calculators; values here are independent implementations.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
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
}

#: Legacy ids with *different* fide-2024 semantics (same id, ruleset
#: namespaces the meaning — documented in docs/TIEBREAK_RULES.md).
REDEFINED_IDS: Tuple[str, ...] = (
    "koya", "aro", "wins", "wins_black", "games_black", "progressive",
)

_UNIMPLEMENTED = ("arpo", "buchholz_sum", "direct_encounter")


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
    """fide-2024 values + explicit-policy ordering (sort_key shared)."""
    from tiebreak_core.ranking import sort_key
    keys = deterministic_keys or {}
    shared = dict(players)
    scored: List[PlayerResult] = []
    for pid, pdata in shared.items():
        values = calculate_all(pdata, shared, list(criteria), total_rounds)
        scored.append(PlayerResult(player_id=pid,
                                   points=pdata.points or 0.0,
                                   values=dict(values), rank=0))

    def _key(pr: PlayerResult) -> Tuple:
        return sort_key(pr.points, pr.values, criteria,
                        keys.get(pr.player_id, pr.player_id))

    ordered = sorted(scored, key=_key)
    ranked = tuple(
        PlayerResult(player_id=pr.player_id, points=pr.points,
                     values=pr.values, rank=i + 1)
        for i, pr in enumerate(ordered))
    return StandingsResult(players=ranked, criteria=tuple(criteria),
                           rules_version=RULESET)
