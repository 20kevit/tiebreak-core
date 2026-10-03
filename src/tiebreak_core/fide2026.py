"""
FIDE-2026 calculation engine (ruleset ``fide-2026``).

Basis (PRIMARY sources):
  - FIDE Council document 2024_FC2_18 (applied 1 Aug 2024) — the
    ``fide-2024`` baseline this engine extends (see
    ``tiebreak_core.fide2024`` module docstring).
  - FIDE Arbiters' Manual 2026, C.07 edition effective 1 Mar 2026
    (approved by FIDE Council 02/02/2026) — word-level diff D1–D15 in
    ``docs/FIDE_2026_DIFF.md``; six official worked examples in
    ``tests/corpus/fide2026_unplayed.json``.

What is new in 2026 (and implemented here):

  - D13/§16.4 dummy caps. Unplayed-round dummies are capped:
    16.4.1 — forfeit rounds (categories 16.2.2, 16.2.4): the dummy's
    score is ``min(own score, scheduled opponent's adjusted score)``;
    16.4.2 — all other unplayed rounds (16.2.1, 16.2.3, 16.2.5):
    ``min(own score, draw-points x tournament rounds)``.
    The ``fide-2024`` engine (uncapped) is frozen and untouched.
  - D12/§15.2 round-robin forfeit carve-out behind an explicit
    ``mode`` flag (``"swiss"`` default | ``"round_robin"``). Swiss
    mode applies Article 16 exactly like ``fide-2024`` plus the
    16.4 caps. Round-robin mode treats forfeit wins/losses against a
    scheduled opponent as regular games, EXCEPT that all forfeits
    remain unplayed in rating-based tie-breaks (Article 10) and
    forfeit losses remain unplayed in Type-B counts (Article 7).
  - MTB26 ``/P`` (forfeit-inclusion opt-in, cf. §6.1.1): the
    ``forfeits_as_played`` flag lets Swiss-mode regulations count
    forfeit wins/losses against a scheduled opponent as regular
    games for BH/SB/FB/Koya contributions and the DE mini-table.
    Rating sets (Article 10) and Type-B counts are unaffected by the
    flag (documented scope; see ``FIDE_TIEBREAK_MODIFIERS.md``).
  - D6/§7.8 TPN and D10/§10.6 RTNG as terminal ranking stages
    (``"tpn"``, ``"rtng"``): deterministic lots-replacements applied
    at the end of a criteria sequence, not scalar values.
  - D7 Article 8 note (Buchholz banned from round-robins): documented
    scope restriction, not enforced (detection needs full pairing
    coverage; see ``KNOWN_LIMITATIONS.md``).
  - D9 §10 preamble (first-rating rule): the core receives a single
    rating snapshot, which is by contract the tournament-start (first)
    list; mid-tournament re-ratings must be resolved consumer-side
    before calling. Compliant by construction; enforced by contract,
    not by code.

Explicitly NOT implemented (see roadmap; requesting them raises
``UnsupportedCriterionError``):
  - D5/§7.7 Standard Points (needs scheduled-opponent round scores +
    the event scoring table — model extension, Phase F26-2).
  - Team systems (§§11–13 incl. D11 EDE chains), Art.16.6 overrides,
    Koya-limit machinery (§14.5).

Terminology: "dummy" below is the FIDE C.07 §16.4 virtual-opponent
concept (a capped/uncapped score standing in for an unplayed round),
NOT the legacy ``opponent_id == -1`` sentinel (see ADR-006).

Adjusted scores sum *recorded* rounds only — identical to
``fide-2024`` (§§16.1–16.3 are word-identical in 2026, D1–D15). A
context-only record with no rounds contributes 0.0; consumers needing
a nonzero scheduled-opponent cap basis must reconstruct that
opponent's history (cf. the EX01 Leo stub), never rely on a
points-fallback (there is none).

Performance: every scalar below accepts an internal ``_pre``
precomputed context ``(ctx, adj)``. ``rank_standings`` builds it ONCE,
so full-tournament ranking is linearithmic in players, not quadratic.
Direct ``calculate`` calls omit ``_pre`` (one O(players) precompute
per call — same shape as ``fide-2024``). ``_pre`` is internal API.

Legacy behavior is untouched: this module never imports or calls the
legacy calculators. ``fide-2024`` helpers are reused only as pure
building blocks (cut operators, rating tables, splitting); every
criterion body here is a local implementation so the context can be
shared — Swiss parity with ``fide-2024`` on fully-played events is
pinned by differential tests, not by delegation.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Mapping, Sequence, Tuple

from tiebreak_core import fide2024 as _f24
from tiebreak_core.errors import UnsupportedCriterionError
from tiebreak_core.models import (
    ABSENT,
    FORFEIT_LOSS,
    FORFEIT_WIN,
    PLAYED,
    PlayerResult,
    PlayerTiebreakData,
    StandingsResult,
    normalize_kind,
)

RULESET = "fide-2026"

MODES: Tuple[str, ...] = ("swiss", "round_robin")

#: Ranking stages that order (not scalar values). Handled by
#: ``rank_standings``; ``calculate`` refuses them (see below).
TERMINAL_CRITERIA: Tuple[str, ...] = ("tpn", "rtng")

_FORFEIT_KINDS = (FORFEIT_WIN, FORFEIT_LOSS)
#: Categories whose dummies are capped by §16.4.1 (forfeits).
_CAP41_CATEGORIES = (_f24.CAT_FW, _f24.CAT_FL)
#: Categories excluded from round-robin REP (requested byes only —
#: forfeits count as elected games under §15.2).
_RR_REP_EXCLUDED = (_f24.CAT_RB_EARLY, _f24.CAT_RB_LATE)

#: Precomputed shared context: (classified rounds, adjusted scores).
_Precomputed = Tuple[Dict[int, List[_f24.ClassifiedRound]],
                     Dict[int, float]]


def _validate_mode(mode: str) -> str:
    if mode not in MODES:
        from tiebreak_core.errors import InvalidPlayerDataError
        raise InvalidPlayerDataError(
            f"fide-2026 mode must be one of {list(MODES)}, got {mode!r}")
    return mode


def _validate_draw_points(draw_points: float) -> float:
    import math
    if (isinstance(draw_points, bool)
            or not isinstance(draw_points, (int, float))
            or not math.isfinite(draw_points)
            or draw_points < 0):
        from tiebreak_core.errors import InvalidPlayerDataError
        raise InvalidPlayerDataError(
            f"fide-2026 draw_points must be a finite number >= 0 "
            f"(0.5 for standard scoring), got {draw_points!r}")
    return float(draw_points)


def _validate_forfeits_flag(forfeits_as_played: bool) -> bool:
    if not isinstance(forfeits_as_played, bool):
        from tiebreak_core.errors import InvalidPlayerDataError
        raise InvalidPlayerDataError(
            f"fide-2026 forfeits_as_played must be bool, got "
            f"{forfeits_as_played!r}")
    return forfeits_as_played


def _precompute(shared: Mapping[int, PlayerTiebreakData],
                total_rounds: int, mode: str,
                draw_points: float) -> _Precomputed:
    """Classify once + adjusted-score table once (shared hot path)."""
    _validate_mode(mode)
    _validate_draw_points(draw_points)
    ctx = _f24._require_context(shared, total_rounds)
    return ctx, _f24._adj_table(shared, ctx)


def _use_pre(shared: Mapping[int, PlayerTiebreakData],
             total_rounds: int, mode: str, draw_points: float,
             _pre: _Precomputed | None) -> _Precomputed:
    if _pre is not None:
        return _pre
    return _precompute(dict(shared), total_rounds, mode, draw_points)


def validate_inputs(players: Mapping[int, PlayerTiebreakData],
                    total_rounds: int) -> None:
    """Same input gate as ``fide-2024`` (uncategorized ``-1`` rounds
    rejected; points must cohere with recorded round scores)."""
    _f24.validate_inputs(players, total_rounds)


# ------------------------------------------------------------------
# §16.4 capped dummies
# ------------------------------------------------------------------

def _scheduled_adjusted(round_: _f24.ClassifiedRound,
                        adj: Mapping[int, float]) -> float | None:
    """Adjusted score of the scheduled opponent (§16.4.1 cap basis).

    Returns ``None`` when the pairing is unknown (``opponent_id == -1``)
    or the opponent is absent from the map — the cap cannot be
    evaluated, so the dummy falls back to the uncapped own score
    (documented edge; FIDE assumes scheduled pairings are known).
    """
    oid = round_.opponent_id
    if oid != -1 and oid in adj:
        return adj[oid]
    return None


def _dummy_value(round_: _f24.ClassifiedRound, own_points: float,
                 adj: Mapping[int, float], draw_points: float,
                 total_rounds: int) -> float:
    """Capped dummy score for one unplayed round (§16.4)."""
    if round_.category in _CAP41_CATEGORIES:
        sched = _scheduled_adjusted(round_, adj)
        if sched is None:
            return own_points
        return min(own_points, sched)
    return min(own_points, draw_points * total_rounds)


def _regular_mode(mode: str, forfeits_as_played: bool) -> str:
    """Effective regime for forfeit-sensitive contributions.

    Round-robin mode always counts scheduled forfeits as regular games
    (§15.2). In Swiss mode the MTB26 ``/P`` opt-in
    (``forfeits_as_played=True``) selects the same treatment for
    BH/SB/FB/Koya contributions and the DE mini-table; Type-B counts
    and rating sets are unaffected (documented scope).
    """
    _validate_forfeits_flag(forfeits_as_played)
    if mode == "round_robin" or forfeits_as_played:
        return "round_robin"
    return "swiss"


def _is_regular_game(kind: str, mode: str, has_scheduled: bool) -> bool:
    """True for rounds contributing as regular games.

    Played rounds always do. In round-robin mode (§15.2, D12) forfeit
    wins/losses against a known scheduled opponent are treated as
    regular games as well.
    """
    if kind == PLAYED:
        return True
    return mode == "round_robin" and kind in _FORFEIT_KINDS and has_scheduled


def _buchholz_contribs(own_points: float,
                       own_rounds: List[_f24.ClassifiedRound],
                       adj: Mapping[int, float], mode: str,
                       draw_points: float,
                       total_rounds: int) -> List[_f24._Contribution]:
    """Buchholz elements with §16.4 capped dummies.

    Played rounds (and RR-mode forfeits vs a scheduled opponent)
    contribute the opponent's adjusted score; every other unplayed
    round contributes the capped dummy. VUR provenance feeds the
    unchanged §16.5 cut exception.
    """
    out: List[_f24._Contribution] = []
    for r in own_rounds:
        sched = r.opponent_id != -1 and r.opponent_id in adj
        if _is_regular_game(r.kind, mode, sched):
            out.append(_f24._Contribution(adj[r.opponent_id], False))
        else:
            out.append(_f24._Contribution(
                _dummy_value(r, own_points, adj, draw_points,
                             total_rounds), r.is_vur))
    return out


def _sb_contribs(own_points: float,
                 own_rounds: List[_f24.ClassifiedRound],
                 adj: Mapping[int, float], mode: str,
                 draw_points: float,
                 total_rounds: int) -> List[_f24._Contribution]:
    """SB elements with §16.4 capped dummies (dummy x round score)."""
    out: List[_f24._Contribution] = []
    for r in own_rounds:
        sched = r.opponent_id != -1 and r.opponent_id in adj
        if _is_regular_game(r.kind, mode, sched):
            out.append(_f24._Contribution(adj[r.opponent_id] * r.score,
                                          False))
        else:
            out.append(_f24._Contribution(
                _dummy_value(r, own_points, adj, draw_points,
                             total_rounds) * r.score, r.is_vur))
    return out


# ------------------------------------------------------------------
# Scalar calculators. Bodies mirror fide-2024 wherever the 2026 text
# is word-identical (verified diff D1–D15); only the dummy legs and
# the RR-mode forfeit scope differ.
# ------------------------------------------------------------------

def buchholz(player: PlayerTiebreakData,
             all_players: Mapping[int, PlayerTiebreakData],
             total_rounds: int, mode: str = "swiss",
             draw_points: float = 0.5,
             forfeits_as_played: bool = False,
             _pre: _Precomputed | None = None) -> float:
    """§8.1 with §§16.3–16.4 (2026 caps). Exact sum (no rounding)."""
    ctx, adj = _use_pre(all_players, total_rounds, mode, draw_points,
                        _pre)
    return _buchholz_core(player, ctx, adj,
                           _regular_mode(mode, forfeits_as_played),
                           draw_points, total_rounds)


def _buchholz_core(player: PlayerTiebreakData, ctx, adj, mode: str,
                   draw_points: float, total_rounds: int) -> float:
    return sum(c.value for c in _buchholz_contribs(
        player.points, ctx[player.player_id], adj, mode, draw_points,
        total_rounds))


def buchholz_cut1(player: PlayerTiebreakData,
                  all_players: Mapping[int, PlayerTiebreakData],
                  total_rounds: int, mode: str = "swiss",
                  draw_points: float = 0.5,
                  forfeits_as_played: bool = False,
                  _pre: _Precomputed | None = None) -> float:
    """BH-C1 §14.1.1.a with §§16.4–16.5.1."""
    ctx, adj = _use_pre(all_players, total_rounds, mode, draw_points,
                        _pre)
    contribs = _buchholz_contribs(player.points, ctx[player.player_id],
                                  adj, _regular_mode(mode, forfeits_as_played), draw_points, total_rounds)
    if len(contribs) < 2:
        return sum(c.value for c in contribs)
    return sum(c.value for c in contribs) - _f24._cut_least_exception(
        contribs)


def buchholz_cut2(player: PlayerTiebreakData,
                  all_players: Mapping[int, PlayerTiebreakData],
                  total_rounds: int, mode: str = "swiss",
                  draw_points: float = 0.5,
                  forfeits_as_played: bool = False,
                  _pre: _Precomputed | None = None) -> float:
    """BH-C2 §14.2 with §§16.4 + 16.5.2 (exception reapplied)."""
    ctx, adj = _use_pre(all_players, total_rounds, mode, draw_points,
                        _pre)
    contribs = _buchholz_contribs(player.points, ctx[player.player_id],
                                  adj, _regular_mode(mode, forfeits_as_played), draw_points, total_rounds)
    if len(contribs) < 2:
        return sum(c.value for c in contribs)
    return sum(c.value for c in _f24._apply_cuts_least(contribs, 2))


def median_buchholz(player: PlayerTiebreakData,
                    all_players: Mapping[int, PlayerTiebreakData],
                    total_rounds: int, mode: str = "swiss",
                    draw_points: float = 0.5,
                    forfeits_as_played: bool = False,
                    _pre: _Precomputed | None = None) -> float:
    """BH-M1 §14.3 with §§16.4–16.5. <3 elements → full BH (edge)."""
    ctx, adj = _use_pre(all_players, total_rounds, mode, draw_points,
                        _pre)
    contribs = _buchholz_contribs(player.points, ctx[player.player_id],
                                  adj, _regular_mode(mode, forfeits_as_played), draw_points, total_rounds)
    if len(contribs) < 3:
        return sum(c.value for c in contribs)
    rest = _f24._apply_cuts_least(contribs, 1)
    return sum(c.value for c in _f24._remove_max(rest))


def median_buchholz_2(player: PlayerTiebreakData,
                      all_players: Mapping[int, PlayerTiebreakData],
                      total_rounds: int, mode: str = "swiss",
                      draw_points: float = 0.5,
                      forfeits_as_played: bool = False,
                      _pre: _Precomputed | None = None) -> float:
    """BH-M2 §14.4 with §§16.4 + 16.5.2. <5 elements → full BH."""
    ctx, adj = _use_pre(all_players, total_rounds, mode, draw_points,
                        _pre)
    contribs = _buchholz_contribs(player.points, ctx[player.player_id],
                                  adj, _regular_mode(mode, forfeits_as_played), draw_points, total_rounds)
    if len(contribs) < 5:
        return sum(c.value for c in contribs)
    rest = _f24._apply_cuts_least(contribs, 2)
    rest = _f24._remove_max(rest)
    return sum(c.value for c in _f24._remove_max(rest))


def sonneborn_berger(player: PlayerTiebreakData,
                     all_players: Mapping[int, PlayerTiebreakData],
                     total_rounds: int, mode: str = "swiss",
                     draw_points: float = 0.5,
                     forfeits_as_played: bool = False,
                     _pre: _Precomputed | None = None) -> float:
    """§9.1 with §§16.3–16.4 (2026 caps). Exact sum (no rounding)."""
    ctx, adj = _use_pre(all_players, total_rounds, mode, draw_points,
                        _pre)
    eff = _regular_mode(mode, forfeits_as_played)
    return sum(c.value for c in _sb_contribs(
        player.points, ctx[player.player_id], adj, eff, draw_points,
        total_rounds))


def sonneborn_berger_cut1(player: PlayerTiebreakData,
                          all_players: Mapping[int, PlayerTiebreakData],
                          total_rounds: int, mode: str = "swiss",
                          draw_points: float = 0.5,
                          forfeits_as_played: bool = False,
                          _pre: _Precomputed | None = None) -> float:
    """SB-C1 §14.1.1.d with §§16.4–16.5.1."""
    ctx, adj = _use_pre(all_players, total_rounds, mode, draw_points,
                        _pre)
    eff = _regular_mode(mode, forfeits_as_played)
    contribs = _sb_contribs(player.points, ctx[player.player_id], adj,
                            eff, draw_points, total_rounds)
    if len(contribs) < 2:
        return sum(c.value for c in contribs)
    vur = [c.value for c in contribs if c.from_vur]
    least = min(c.value for c in contribs)
    cut = max(min(vur), least) if vur else least
    remaining = list(contribs)
    remaining.remove(next(c for c in remaining if c.value == cut))
    return sum(c.value for c in remaining)


def fore_buchholz(player: PlayerTiebreakData,
                  all_players: Mapping[int, PlayerTiebreakData],
                  total_rounds: int, mode: str = "swiss",
                  draw_points: float = 0.5,
                  forfeits_as_played: bool = False,
                  _pre: _Precomputed | None = None) -> float:
    """FB §8.3 with §16.4 caps on the dummy legs.

    Final-round *paired* games count as draws; unpaired final rounds
    keep awarded points; Article 16 applies on top with the dummy rule
    using FB-adjusted own points (capped per 16.4.1/16.4.2).
    """
    ctx, _adj = _use_pre(all_players, total_rounds, mode, draw_points,
                         _pre)
    eff = _regular_mode(mode, forfeits_as_played)

    def fb_own(pid: int) -> float:
        pts = 0.0
        for r in ctx[pid]:
            if r.kind == PLAYED and r.round_number == total_rounds:
                pts += 0.5
            else:
                pts += r.score
        return pts

    def fb_adj(pid: int) -> float:
        total = 0.0
        for r in ctx[pid]:
            if r.category == _f24.CAT_RB_LATE:
                total += 0.5
            elif r.kind == PLAYED and r.round_number == total_rounds:
                total += 0.5
            else:
                total += r.score
        return total

    own_fb = fb_own(player.player_id)
    adj = {pid: fb_adj(pid) for pid in all_players}
    total = 0.0
    for r in ctx[player.player_id]:
        sched = r.opponent_id != -1 and r.opponent_id in adj
        if _is_regular_game(r.kind, eff, sched):
            total += adj[r.opponent_id]
        else:
            total += _dummy_value(r, own_fb, adj, draw_points,
                                  total_rounds)
    return total


def average_opponents_buchholz(
        player: PlayerTiebreakData,
        all_players: Mapping[int, PlayerTiebreakData],
        total_rounds: int, mode: str = "swiss",
        draw_points: float = 0.5,
        forfeits_as_played: bool = False,
        _pre: _Precomputed | None = None) -> float:
    """AOB §8.2: average of OTB opponents' (fide-2026) Buchholz.

    Rounded to 1 decimal (documented presentation choice; FIDE states
    no rounding for AOB). Empty set → 0.0. An FB-based variant (D8
    "(or Fore Buchholz)") would be a new criterion id, not a silent
    change — this id averages BH.
    """
    ctx, adj = _use_pre(all_players, total_rounds, mode, draw_points,
                        _pre)
    shared = dict(all_players)
    opp_ids = [r.opponent_id for r in ctx[player.player_id]
               if r.kind == PLAYED and r.opponent_id in shared]
    if not opp_ids:
        return 0.0
    eff = _regular_mode(mode, forfeits_as_played)
    bhs = [_buchholz_core(shared[oid], ctx, adj, eff, draw_points,
                           total_rounds) for oid in opp_ids]
    return round(sum(bhs) / len(bhs), 1)


# --- Type-B / progressive / Koya (D12-aware; Swiss legs mirror 2024). ---

def _rr_typeb_games(player: PlayerTiebreakData,
                    ctx: Dict[int, List[_f24.ClassifiedRound]],
                    all_players: Mapping[int, PlayerTiebreakData]
                    ) -> List[object]:
    """Game records counting for Type-B counts in RR mode (§15.2).

    Played games plus forfeit WINS against a known scheduled opponent
    ("treated as regular games"); forfeit LOSSES remain unplayed in
    Type B (§15.2 carve-out, D12) and are excluded here.
    """
    by_round = {g.round_number: g for g in player.games}
    out = []
    for r in ctx[player.player_id]:
        if r.kind == PLAYED:
            out.append(by_round.get(r.round_number))
        elif (r.kind == FORFEIT_WIN and r.opponent_id != -1
                and r.opponent_id in all_players):
            out.append(by_round.get(r.round_number))
    return out


def wins(player: PlayerTiebreakData,
         all_players: Mapping[int, PlayerTiebreakData],
         total_rounds: int, mode: str = "swiss",
         draw_points: float = 0.5,
         forfeits_as_played: bool = False,
         _pre: _Precomputed | None = None) -> float:
    """WIN §7.1: rounds with win-points, with or without playing."""
    _validate_forfeits_flag(forfeits_as_played)
    ctx, _ = _use_pre(all_players, total_rounds, mode, draw_points,
                      _pre)
    return float(sum(1 for r in ctx[player.player_id] if r.score == 1.0))


def won(player: PlayerTiebreakData,
        all_players: Mapping[int, PlayerTiebreakData],
        total_rounds: int, mode: str = "swiss",
        draw_points: float = 0.5,
        forfeits_as_played: bool = False,
        _pre: _Precomputed | None = None) -> float:
    """WON §7.2: games won over the board (RR: + forfeit wins, §15.2)."""
    _validate_forfeits_flag(forfeits_as_played)
    if mode == "swiss":
        _use_pre(all_players, total_rounds, mode, draw_points, _pre)
        return float(sum(1 for g in player.games
                         if normalize_kind(g) == PLAYED
                         and g.score == 1.0))
    ctx, _ = _use_pre(all_players, total_rounds, mode, draw_points,
                      _pre)
    games = _rr_typeb_games(player, ctx, all_players)
    return float(sum(1 for g in games
                     if g is not None and g.score == 1.0))


def games_black(player: PlayerTiebreakData,
                all_players: Mapping[int, PlayerTiebreakData],
                total_rounds: int, mode: str = "swiss",
                draw_points: float = 0.5,
                forfeits_as_played: bool = False,
                _pre: _Precomputed | None = None) -> float:
    """BPG §7.3 (RR: forfeit wins count as games, losses excluded)."""
    _validate_forfeits_flag(forfeits_as_played)
    if mode == "swiss":
        _use_pre(all_players, total_rounds, mode, draw_points, _pre)
        return float(sum(1 for g in player.games
                         if normalize_kind(g) == PLAYED
                         and g.color == "black"))
    ctx, _ = _use_pre(all_players, total_rounds, mode, draw_points,
                      _pre)
    games = _rr_typeb_games(player, ctx, all_players)
    return float(sum(1 for g in games
                     if g is not None and g.color == "black"))


def wins_black(player: PlayerTiebreakData,
               all_players: Mapping[int, PlayerTiebreakData],
               total_rounds: int, mode: str = "swiss",
               draw_points: float = 0.5,
               forfeits_as_played: bool = False,
               _pre: _Precomputed | None = None) -> float:
    """BWG §7.4 (RR: forfeit wins with black count, §15.2)."""
    _validate_forfeits_flag(forfeits_as_played)
    if mode == "swiss":
        _use_pre(all_players, total_rounds, mode, draw_points, _pre)
        return float(sum(1 for g in player.games
                         if normalize_kind(g) == PLAYED
                         and g.color == "black" and g.score == 1.0))
    ctx, _ = _use_pre(all_players, total_rounds, mode, draw_points,
                      _pre)
    games = _rr_typeb_games(player, ctx, all_players)
    return float(sum(1 for g in games if g is not None
                     and g.color == "black" and g.score == 1.0))


def rounds_played_elected(
        player: PlayerTiebreakData,
        all_players: Mapping[int, PlayerTiebreakData],
        total_rounds: int, mode: str = "swiss",
        draw_points: float = 0.5,
        forfeits_as_played: bool = False,
        _pre: _Precomputed | None = None) -> float:
    """REP §7.6.

    Swiss: recorded non-absent rounds minus half/zero-byes and forfeit
    losses. RR: forfeits count as elected (§15.2);     only requested byes
    are excluded.
    """
    _validate_forfeits_flag(forfeits_as_played)
    ctx, _ = _use_pre(all_players, total_rounds, mode, draw_points,
                      _pre)
    rounds = [r for r in ctx[player.player_id] if r.kind != ABSENT]
    if mode == "swiss":
        excluded = sum(1 for r in rounds if r.is_vur)
    else:
        excluded = sum(1 for r in rounds
                       if r.category in _RR_REP_EXCLUDED)
    return float(len(rounds) - excluded)


def progressive(player: PlayerTiebreakData,
                all_players: Mapping[int, PlayerTiebreakData],
                total_rounds: int, mode: str = "swiss",
                draw_points: float = 0.5,
                forfeits_as_played: bool = False,
                _pre: _Precomputed | None = None) -> float:
    """§7.5 over all tournament rounds (gap-filled; absent carries)."""
    _validate_forfeits_flag(forfeits_as_played)
    ctx, _ = _use_pre(all_players, total_rounds, mode, draw_points,
                      _pre)
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
                     total_rounds: int, mode: str = "swiss",
                     draw_points: float = 0.5,
                     forfeits_as_played: bool = False,
                     _pre: _Precomputed | None = None) -> float:
    """PS-C1 §14.1.1.c: exclude the score achieved after round one."""
    _validate_forfeits_flag(forfeits_as_played)
    ctx, _ = _use_pre(all_players, total_rounds, mode, draw_points,
                      _pre)
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


def koya(player: PlayerTiebreakData,
         all_players: Mapping[int, PlayerTiebreakData],
         total_rounds: int, mode: str = "swiss",
         draw_points: float = 0.5,
         forfeits_as_played: bool = False,
         _pre: _Precomputed | None = None) -> float:
    """KS §9.2: points vs opponents on ≥50% of the maximum possible.

    Maximum possible = total tournament rounds. Not Art.16-managed:
    opponent qualification uses raw final points. In RR mode forfeit
    results vs scheduled opponents count (§15.2); the rating-family
    exclusion does not apply here (not Article 10).
    """
    _use_pre(all_players, total_rounds, mode, draw_points, _pre)
    eff = _regular_mode(mode, forfeits_as_played)
    threshold = total_rounds / 2
    total = 0.0
    for g in player.games:
        kind = normalize_kind(g)
        sched = g.opponent_id != -1 and g.opponent_id in all_players
        if not _is_regular_game(kind, eff, sched):
            continue
        if g.opponent_id not in all_players:
            continue
        if all_players[g.opponent_id].points >= threshold:
            total += g.score
    return total


# --- Rating family (D9/D12-compliant in both modes: rated OTB only). ---

def _otb_rated_opponents(player: PlayerTiebreakData,
                         all_players: Mapping[int, PlayerTiebreakData]
                         ) -> List[PlayerTiebreakData]:
    out = []
    for g in player.games:
        if normalize_kind(g) != PLAYED or g.opponent_id not in all_players:
            continue
        opp = all_players[g.opponent_id]
        if opp.rating > 0:
            out.append(opp)
    return out


def average_rating_opponents(
        player: PlayerTiebreakData,
        all_players: Mapping[int, PlayerTiebreakData],
        total_rounds: int, mode: str = "swiss",
        draw_points: float = 0.5,
        forfeits_as_played: bool = False,
        _pre: _Precomputed | None = None) -> float:
    """ARO §10.1: average of rated OTB opponents, 0.5 rounded up.

    Opponents without a positive rating are excluded. Empty set → 0.0
    (documented edge).
    """
    _validate_forfeits_flag(forfeits_as_played)
    _use_pre(all_players, total_rounds, mode, draw_points, _pre)
    opps = _otb_rated_opponents(player, all_players)
    if not opps:
        return 0.0
    return float(_f24._fide_round_half_up(
        sum(o.rating for o in opps) / len(opps)))


def aro_cut1(player: PlayerTiebreakData,
             all_players: Mapping[int, PlayerTiebreakData],
             total_rounds: int, mode: str = "swiss",
             draw_points: float = 0.5,
             forfeits_as_played: bool = False,
             _pre: _Precomputed | None = None) -> float:
    """ARO-C1 §14.1.1.b: exclude the lowest opponent rating.

    VUR rounds contribute no opponent rating, so the §16.5 exception
    has no element to prefer; the plain lowest rating is cut. Fewer
    than 2 rated OTB opponents → uncut ARO (documented edge).
    """
    _validate_forfeits_flag(forfeits_as_played)
    _use_pre(all_players, total_rounds, mode, draw_points, _pre)
    opps = sorted(_otb_rated_opponents(player, all_players),
                  key=lambda o: o.rating)
    if len(opps) < 2:
        if not opps:
            return 0.0
        return float(_f24._fide_round_half_up(
            sum(o.rating for o in opps) / len(opps)))
    rest = opps[1:]
    return float(_f24._fide_round_half_up(
        sum(o.rating for o in rest) / len(rest)))


def _tpr_core(games: List[Tuple[float, int]]) -> float:
    """Tournament performance from rated-OTB (score, opp rating) pairs."""
    if not games:
        return 0.0
    aro = _f24._fide_round_half_up(sum(r for _, r in games) / len(games))
    points = sum(s for s, _ in games)
    return float(aro + _f24._dp_for_fraction(points, len(games)))


def tournament_performance(
        player: PlayerTiebreakData,
        all_players: Mapping[int, PlayerTiebreakData],
        total_rounds: int, mode: str = "swiss",
        draw_points: float = 0.5,
        forfeits_as_played: bool = False,
        _pre: _Precomputed | None = None) -> float:
    """TPR §10.2: rounded ARO + table rating difference.

    The fraction is points in rated OTB games over their count. No
    rated OTB games → 0.0 (documented edge, consistent with ARO).
    """
    _validate_forfeits_flag(forfeits_as_played)
    _use_pre(all_players, total_rounds, mode, draw_points, _pre)
    return _tpr_core(_f24._rated_otb_games(player, all_players))


def _ptp_core(games: List[Tuple[float, int]]) -> float:
    """Perfect performance from rated-OTB (score, opp rating) pairs."""
    if not games:
        return 0.0
    target = sum(s for s, _ in games)
    lowest = min(r for _, r in games)
    if target <= 0:
        return float(lowest - 800)

    def expected(rating: int) -> float:
        return sum(_f24._pd_for_rating(rating, opp) for _, opp in games)

    lo = lowest - 800
    hi = max(r for _, r in games) + 800
    while lo < hi:
        mid = (lo + hi) // 2
        if expected(mid) >= target:
            hi = mid
        else:
            lo = mid + 1
    return float(lo)


def perfect_performance(
        player: PlayerTiebreakData,
        all_players: Mapping[int, PlayerTiebreakData],
        total_rounds: int, mode: str = "swiss",
        draw_points: float = 0.5,
        forfeits_as_played: bool = False,
        _pre: _Precomputed | None = None) -> float:
    """PTP §10.3: lowest rating with expected score ≥ tournament score.

    Zero target → 800 below the lowest rated opponent (per spec). No
    rated OTB games → 0.0.
    """
    _validate_forfeits_flag(forfeits_as_played)
    _use_pre(all_players, total_rounds, mode, draw_points, _pre)
    return _ptp_core(_f24._rated_otb_games(player, all_players))


def _average_opponent_metric(
        player: PlayerTiebreakData,
        all_players: Mapping[int, PlayerTiebreakData],
        core) -> float:
    """Mean of a rating ``core`` over OTB opponents (§§10.4–10.5 shape)."""
    opps = [g.opponent_id for g in player.games
            if normalize_kind(g) == PLAYED
            and g.opponent_id in all_players]
    if not opps:
        return 0.0
    vals = [core(_f24._rated_otb_games(all_players[oid], all_players))
            for oid in opps]
    return float(_f24._fide_round_half_up(sum(vals) / len(vals)))


def apro(player: PlayerTiebreakData,
         all_players: Mapping[int, PlayerTiebreakData],
         total_rounds: int, mode: str = "swiss",
         draw_points: float = 0.5,
         forfeits_as_played: bool = False,
         _pre: _Precomputed | None = None) -> float:
    """APRO §10.4: average of OTB opponents' TPR, 0.5 rounded up."""
    _validate_forfeits_flag(forfeits_as_played)
    _use_pre(all_players, total_rounds, mode, draw_points, _pre)
    return _average_opponent_metric(player, all_players, _tpr_core)


def appo(player: PlayerTiebreakData,
         all_players: Mapping[int, PlayerTiebreakData],
         total_rounds: int, mode: str = "swiss",
         draw_points: float = 0.5,
         forfeits_as_played: bool = False,
         _pre: _Precomputed | None = None) -> float:
    """APPO §10.5: average of OTB opponents' PTP, 0.5 rounded up."""
    _validate_forfeits_flag(forfeits_as_played)
    _use_pre(all_players, total_rounds, mode, draw_points, _pre)
    return _average_opponent_metric(player, all_players, _ptp_core)


# ------------------------------------------------------------------
# Registry, dispatcher, ranking
# ------------------------------------------------------------------

FIDE2026_IDS: Tuple[str, ...] = (
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

FIDE2026_REGISTRY = {
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

#: Group-level (non-scalar) ranking stages (same §§6.1–6.3; D4).
GROUP_CRITERIA: Tuple[str, ...] = ("direct_encounter",)


def is_supported_criterion(criterion: str) -> bool:
    """True iff ``criterion`` is usable under fide-2026 (scalar or a
    ranking stage: group-level DE or terminal TPN/RTNG)."""
    return (criterion in FIDE2026_REGISTRY
            or criterion in GROUP_CRITERIA
            or criterion in TERMINAL_CRITERIA)


def require_supported(criterion: str, *, for_ranking: bool = False) -> None:
    """Raise for ids unknown or unimplemented under fide-2026.

    Terminal stages (``tpn``/``rtng``) are ranking-only: requesting a
    scalar value for them raises ``UnsupportedCriterionError`` with a
    pointer to ``rank_standings``.
    """
    from tiebreak_core.registry import is_known
    if criterion in TERMINAL_CRITERIA and not for_ranking:
        raise UnsupportedCriterionError(
            f"{criterion} (terminal ranking key under {RULESET}; "
            f"use rank_standings, not calculate)", RULESET)
    if not is_known(criterion) and criterion not in FIDE2026_REGISTRY:
        from tiebreak_core.errors import UnknownCriterionError
        raise UnknownCriterionError(criterion)
    if criterion not in FIDE2026_REGISTRY and not for_ranking:
        raise UnsupportedCriterionError(criterion, RULESET)


def calculate(player: PlayerTiebreakData,
              all_players: Mapping[int, PlayerTiebreakData],
              criterion: str, total_rounds: int,
              mode: str = "swiss", draw_points: float = 0.5,
              forfeits_as_played: bool = False) -> float:
    """Single fide-2026 calculation (validated upstream by strict)."""
    require_supported(criterion)
    _validate_forfeits_flag(forfeits_as_played)
    return FIDE2026_REGISTRY[criterion](player, dict(all_players),
                                        total_rounds, mode,
                                        draw_points, forfeits_as_played)


def calculate_all(player: PlayerTiebreakData,
                  all_players: Mapping[int, PlayerTiebreakData],
                  criteria: Sequence[str], total_rounds: int,
                  mode: str = "swiss",
                  draw_points: float = 0.5,
                  forfeits_as_played: bool = False) -> Dict[str, float]:
    """Multi-criterion fide-2026 calculation."""
    _validate_forfeits_flag(forfeits_as_played)
    return {c: calculate(player, all_players, c, total_rounds, mode,
                         draw_points, forfeits_as_played)
            for c in criteria}


def check_ranking_criteria(criteria: Sequence[str]) -> None:
    """Validate a ranking criteria sequence (scalars + DE + terminals)."""
    for criterion in criteria:
        if criterion in GROUP_CRITERIA or criterion in TERMINAL_CRITERIA:
            continue
        require_supported(criterion, for_ranking=True)


def _validate_pairing_numbers(
        pairing_numbers: Mapping[int, int] | None,
        players: Mapping[int, PlayerTiebreakData]) -> Dict[int, int]:
    from tiebreak_core.errors import InvalidPlayerDataError
    if pairing_numbers is None:
        raise InvalidPlayerDataError(
            "fide-2026 criterion 'tpn' requires pairing_numbers "
            "(final tournament pairing numbers per player id)")
    if not isinstance(pairing_numbers, Mapping):
        raise InvalidPlayerDataError("pairing_numbers must be a mapping")
    checked: Dict[int, int] = {}
    for key, value in pairing_numbers.items():
        if (isinstance(key, bool) or not isinstance(key, int)
                or isinstance(value, bool) or not isinstance(value, int)
                or value < 1):
            raise InvalidPlayerDataError(
                "pairing_numbers must map int player id -> int >= 1")
        checked[key] = value
    missing = [pid for pid in players if pid not in checked]
    if missing:
        raise InvalidPlayerDataError(
            f"pairing_numbers missing entries for players {missing}")
    return checked


def rank_standings(players: Mapping[int, PlayerTiebreakData],
                   criteria: Sequence[str], total_rounds: int,
                   deterministic_keys: Mapping[int, int] | None = None,
                   mode: str = "swiss", draw_points: float = 0.5,
                   pairing_numbers: Mapping[int, int] | None = None,
                   forfeits_as_played: bool = False,
                   ) -> StandingsResult:
    """fide-2026 values + staged ordering (points, then criteria).

    Scalar criteria split groups by value (descending); the group-level
    ``direct_encounter`` resolves tied groups per §§6.1–6.3 (unchanged
    in 2026, D4); terminal ``tpn`` orders by final pairing number
    ascending (§7.8) and ``rtng`` by rating descending (§10.6).
    Unresolvable groups fall back to ``deterministic_keys`` (pre-sorted,
    so every stage is stable). ``values`` carries scalar criteria only.

    The classification + adjusted-score context is built once and
    shared by every scalar evaluation (linearithmic ranking).
    """
    shared = dict(players)
    _validate_forfeits_flag(forfeits_as_played)
    pre = _precompute(shared, total_rounds, mode, draw_points)
    check_ranking_criteria(criteria)
    keys = deterministic_keys or {}
    tpn = _validate_pairing_numbers(pairing_numbers, shared) \
        if "tpn" in criteria else {}
    ordered_ids = sorted(shared, key=lambda pid: keys.get(pid, pid))
    scalar = [c for c in criteria if c in FIDE2026_REGISTRY]
    values: Dict[int, Dict[str, float]] = {
        pid: {c: FIDE2026_REGISTRY[c](shared[pid], shared, total_rounds,
                                      mode, draw_points,
                                      forfeits_as_played, pre)
              for c in scalar}
        for pid in ordered_ids
    }
    eff = _regular_mode(mode, forfeits_as_played)
    groups: List[List[int]] = _f24._split_by(
        [ordered_ids], lambda pid: -(shared[pid].points or 0.0))
    for criterion in criteria:
        if criterion in GROUP_CRITERIA:
            groups = [tier for g in groups
                      for tier in _de_tiers(g, shared, eff)]
        elif criterion == "tpn":
            groups = _f24._split_by(groups, lambda pid: tpn[pid])
        elif criterion == "rtng":
            groups = _f24._split_by(
                groups, lambda pid: -(shared[pid].rating or 0))
        else:
            groups = _f24._split_by(
                groups, lambda pid: -values[pid][criterion])
    flat = [pid for g in groups for pid in g]
    ranked = tuple(
        PlayerResult(player_id=pid, points=shared[pid].points or 0.0,
                     values=dict(values[pid]), rank=i + 1)
        for i, pid in enumerate(flat))
    return StandingsResult(players=ranked, criteria=tuple(criteria),
                           rules_version=RULESET)


# ------------------------------------------------------------------
# Direct Encounter §§6.1–6.3 (group-level). Unchanged in 2026 (D4);
# round-robin mode includes forfeit results as regular games (§15.2).
# ------------------------------------------------------------------

def _mini_table(group: Sequence[int],
                players: Mapping[int, PlayerTiebreakData],
                mode: str) -> Tuple[Dict[int, Fraction], Dict[int, int]]:
    """Mini-standings over a tied group (§6.1).

    Swiss: only ``played`` games count; forfeits excluded (§6.1.1).
    Round-robin: forfeit wins/losses count as regular games (§15.2).
    Repeated meetings average per side (§6.1.2). A pair counts as
    unplayed when NO game record exists between them in either
    direction (documented interpretation).
    """
    gset = set(group)
    scores: Dict[int, Fraction] = {pid: Fraction(0) for pid in group}
    missing: Dict[int, int] = {pid: 0 for pid in group}
    done = set()
    for pid in group:
        own = [g for g in players[pid].games
               if g.opponent_id in gset and g.opponent_id != pid
               and (normalize_kind(g) == PLAYED
                    or (mode == "round_robin"
                        and normalize_kind(g) in _FORFEIT_KINDS))]
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
              players: Mapping[int, PlayerTiebreakData],
              mode: str) -> List[List[int]]:
    """Resolve one tied group per §6 into ordered tiers (best first).

    All-met groups follow §6.2 (mini-table order, recursive reapplication
    to tied subsets). Otherwise §6.3 certainty ranking applies
    iteratively; whatever remains unresolvable is returned as one tier
    (falls through to subsequent criteria).
    """
    if len(group) <= 1:
        return [list(group)]
    scores, missing = _mini_table(group, players, mode)
    if all(missing[pid] == 0 for pid in group):
        tiers: List[List[int]] = []
        bucket: Dict[Fraction, List[int]] = {}
        for pid in group:
            bucket.setdefault(scores[pid], []).append(pid)
        for score in sorted(bucket, reverse=True):
            tied = bucket[score]
            if len(tied) == 1 or len(tied) == len(group):
                tiers.append(tied)
            else:
                tiers.extend(_de_tiers(tied, players, mode))  # §6.2
        return tiers
    remaining = list(group)
    tiers = []
    while remaining:
        scores_r, missing_r = _mini_table(remaining, players, mode)
        first = None
        for candidate in remaining:
            if all(scores_r[candidate]
                   > scores_r[other] + missing_r[other]
                   for other in remaining if other != candidate):
                first = candidate
                break
        if first is None:
            tiers.append(list(remaining))
            break
        tiers.append([first])
        remaining.remove(first)
    return tiers
