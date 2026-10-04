"""
Generic MTB26 modifier engine (ruleset ``fide-2026`` individual scope).

MTB26 (``docs/FIDE_MTB26_CATALOG.md``) lists tie-break *codes* such as
``BH/C3``, ``ARO/M5``, ``KS/L-1`` where ``x`` means "any reasonable
value must be implemented". The named combinations (C1/C2/M1/M2) live
as fixed criterion ids in ``tiebreak_core.fide2026``; this module is
the generic machine behind them:

- :func:`parse_descriptor` — case-insensitive MTB26 rank-order
  descriptor grammar ``Name[:MP|:GP][/Cn][/Mn][/L±n][/Kx][/P][/F][/R]``
  into a :class:`ModifierSpec`. Invalid combinations (e.g. ``SB/M1``,
  ``KS/P``) are rejected with :class:`InvalidDescriptorError`.
- Generic calculators for arbitrary valid ``n`` (cuts, medians,
  Koya limits, PS round-exclusions). ``n == 1`` / ``n == 2`` reproduce
  the named ids exactly (pinned by equivalence tests); the engine
  delegates to the named implementations there, so there is exactly
  one code path per named semantic.
- :func:`calculate_descriptor` / :func:`rank_descriptors` — normalized
  (non-stringly) entry points: callers pass descriptors, the core
  resolves semantics + flags. Team codes (``:MP``/``:GP`` refs and
  team-only bases) resolve through ``tiebreak_core.team``.

Evidence levels: descriptor grammar + variant permissions are
PRIMARY_NORMATIVE (MTB26 code table, retrieved 2026-10-03; C.07
Articles 13–14). PS/Cn (n >= 2) generalizes §14.1.1.c round-exclusion
(MTB26-machine reading, documented); SB/Cn (n >= 3) reapplies the
§14.1.1.d + §16.5.1 victim rule per §16.5.2 (documented).

Frozen rulesets are untouched: ``fide-2024`` keeps its named ids
(generic ``n >= 3`` descriptors resolve under ``fide-2026`` only).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Sequence, Tuple

from tiebreak_core.errors import (
    InvalidDescriptorError,
    UnsupportedCriterionError,
)

# ------------------------------------------------------------------
# Descriptor model
# ------------------------------------------------------------------

#: Individual bases (C.07 Arts. 6–10; acronym -> canonical criterion stem).
_INDIVIDUAL_BASES: Dict[str, str] = {
    "DE": "direct_encounter",
    "BPG": "games_black",
    "BWG": "wins_black",
    "REP": "rounds_elected",
    "STD": "std",
    "WIN": "wins",
    "WON": "won",
    "PS": "progressive",
    "TPN": "tpn",
    "BH": "buchholz",
    "AOB": "aob",
    "FB": "fore_buchholz",
    "SB": "sonneborn_berger",
    "KS": "koya",
    "ARO": "aro",
    "TPR": "tpr",
    "PTP": "ptp",
    "APRO": "apro",
    "APPO": "appo",
    "RTNG": "rtng",
}

#: Team-only bases (resolved via tiebreak_core.team; acronym set only).
_TEAM_BASES = (
    "BC", "TBR", "BBE", "MPVGP",
    "EMMSB", "EMGSB", "EGMSB", "EGGSB",
    "EDE", "EDEBT", "EDEBB", "EDET", "EDEB",
    "SSSC",
)

#: Table-2 bases reusable for teams with a :MP/:GP reference score.
_TEAM_REF_BASES = ("WIN", "WON", "PS", "BH", "AOB", "FB", "KS")

#: Which individual bases accept /Cn (MTB26 code table, Tables 1–2).
_CUT_BASES = ("BH", "SB", "PS", "ARO", "FB")
#: Which individual bases accept /Mn.
_MEDIAN_BASES = ("BH", "ARO", "FB")

_MAX_GENERIC_N = 64


@dataclass(frozen=True)
class ModifierSpec:
    """Parsed MTB26 descriptor (normalized, semantic — not a string)."""

    base: str            # canonical uppercase acronym, e.g. "BH"
    team_score: str | None  # "MP" / "GP" / None
    cut: int | None      # /Cn
    median: int | None   # /Mn
    limit_halves: int    # /L±n in half-points (KS only), 0 = absent
    sssc_k: int | None   # /Kx (SSSC only)
    forfeits_played: bool  # /P
    fore: bool           # /F
    reverse: bool        # /R

    @property
    def is_team(self) -> bool:
        """True iff this descriptor needs the team module."""
        return self.base in _TEAM_BASES or self.team_score is not None


def _fail(descriptor: object, reason: str) -> None:
    raise InvalidDescriptorError(descriptor, reason)


def parse_descriptor(descriptor: str) -> ModifierSpec:
    """Parse an MTB26 rank-order descriptor into a :class:`ModifierSpec`.

    Grammar (case-insensitive, whitespace-trimmed)::

        Name[:MP|:GP][/Cn][/Mn][/L±n][/Kx][/P][/F][/R]

    Raises :class:`InvalidDescriptorError` for malformed descriptors
    and for modifier combinations FIDE does not define (e.g. ``SB/M1``,
    ``KS/P``, ``AOB/C1``, ``BH/R``, ``TPN/C1``).
    """
    if not isinstance(descriptor, str) or not descriptor.strip():
        _fail(descriptor, "must be a non-empty string")
    text = descriptor.strip().upper()
    parts = text.split("/")
    head = parts[0]
    if ":" in head:
        base, ref = head.split(":", 1)
        if ref not in ("MP", "GP"):
            _fail(descriptor, f"unknown team reference score ':{ref}' "
                              f"(expected :MP or :GP)")
        team_score: str | None = ref
    else:
        base, team_score = head, None
    if base not in _INDIVIDUAL_BASES and base not in _TEAM_BASES:
        _fail(descriptor, f"unknown base {base!r}")
    if team_score is not None and base not in _TEAM_REF_BASES:
        _fail(descriptor, f"base {base!r} does not accept a :MP/:GP "
                          f"team reference score")
    cut: int | None = None
    median: int | None = None
    limit_halves = 0
    sssc_k: int | None = None
    forfeits_played = False
    fore = False
    reverse = False
    seen: set = set()
    for variant in parts[1:]:
        if not variant:
            _fail(descriptor, "empty variant segment (trailing or double '/')")
        tag = variant[0]
        if tag == "C":
            if cut is not None:
                _fail(descriptor, "duplicate /C variant")
            cut = _parse_n(descriptor, variant, 1, "C")
        elif tag == "M":
            if median is not None:
                _fail(descriptor, "duplicate /M variant")
            median = _parse_n(descriptor, variant, 1, "M")
        elif tag == "L":
            if limit_halves != 0:
                _fail(descriptor, "duplicate /L variant")
            limit_halves = _parse_signed(descriptor, variant)
        elif tag == "K":
            if sssc_k is not None:
                _fail(descriptor, "duplicate /K variant")
            sssc_k = _parse_n(descriptor, variant, 1, "K")
        elif variant in ("P", "F", "R"):
            if variant in seen:
                _fail(descriptor, f"duplicate /{variant} variant")
            seen.add(variant)
            if variant == "P":
                forfeits_played = True
            elif variant == "F":
                fore = True
            else:
                reverse = True
        else:
            _fail(descriptor, f"unknown variant '/{variant}'")
    _check_combination(descriptor, base, team_score, cut, median,
                       limit_halves, sssc_k, forfeits_played, fore,
                       reverse)
    return ModifierSpec(base=base, team_score=team_score, cut=cut,
                        median=median, limit_halves=limit_halves,
                        sssc_k=sssc_k,
                        forfeits_played=forfeits_played, fore=fore,
                        reverse=reverse)


def _parse_n(descriptor: object, variant: str, lo: int,
             tag: str) -> int:
    digits = variant[1:]
    if not digits.isdigit():
        _fail(descriptor, f"/{tag}n requires a positive integer, "
                          f"got '/{variant}'")
    n = int(digits)
    if not (lo <= n <= _MAX_GENERIC_N):
        _fail(descriptor, f"/{tag}n out of range [{lo}..{_MAX_GENERIC_N}], "
                          f"got {n}")
    if len(digits) > 1 and digits.startswith("0"):
        _fail(descriptor, f"/{tag}n must not have leading zeros: '/{variant}'")
    return n


def _parse_signed(descriptor: object, variant: str) -> int:
    digits = variant[1:]
    sign = 1
    if digits[:1] in ("+", "-"):
        sign = 1 if digits[0] == "+" else -1
        digits = digits[1:]
    if not digits.isdigit():
        _fail(descriptor, f"/L requires a signed integer (half-points), "
                          f"got '/{variant}'")
    n = sign * int(digits)
    if n == 0 or not (-_MAX_GENERIC_N <= n <= _MAX_GENERIC_N):
        _fail(descriptor, f"/L out of range "
                          f"[±1..±{_MAX_GENERIC_N}] half-points, got {n}")
    return n


def _check_combination(descriptor: object, base: str,
                       team_score: str | None, cut: int | None,
                       median: int | None, limit_halves: int,
                       sssc_k: int | None, forfeits_played: bool,
                       fore: bool, reverse: bool) -> None:
    if cut is not None and median is not None:
        _fail(descriptor, "modifiers /C and /M are mutually exclusive")
    if base in _TEAM_BASES:
        # Team-side permissions mirror the MTB26 Table-3 columns
        # (C1 C2 Kx P F); enforced here at parse time (and re-checked
        # in tiebreak_core.team at resolve time).
        if base in ("BC", "TBR", "BBE", "MPVGP"):
            if (cut is not None or median is not None or limit_halves
                    or sssc_k is not None or forfeits_played or fore):
                _fail(descriptor, f"base {base!r} accepts no variants "
                                  f"(MTB26 Table 3)")
        elif base in ("EMMSB", "EMGSB", "EGMSB", "EGGSB"):
            if (median is not None or limit_halves
                    or sssc_k is not None or fore):
                _fail(descriptor, f"base {base!r} accepts /C1 /C2 /P "
                                  f"only (MTB26 Table 3)")
            if cut is not None and cut > 2:
                _fail(descriptor, f"base {base!r} accepts /C1 /C2 "
                                  f"only — FIDE names no ESB-C{cut}")
        elif base in ("EDE", "EDEBT", "EDEBB", "EDET", "EDEB"):
            if (cut is not None or median is not None or limit_halves
                    or sssc_k is not None or fore):
                _fail(descriptor, f"base {base!r} accepts /P only "
                                  f"(MTB26 Table 3)")
        elif base == "SSSC":
            if median is not None or limit_halves:
                _fail(descriptor, f"base {base!r} accepts /C /K /P /F "
                                  f"only (MTB26 Table 3)")
            if cut is not None and cut > 2:
                _fail(descriptor, f"base {base!r} accepts /C1 /C2 "
                                  f"only in the code table")
        if reverse:
            _fail(descriptor, f"base {base!r} does not accept /R")
        return
    # Individual bases from here on.
    if team_score is not None:
        # :MP/:GP team instantiations resolve via the team module;
        # variant permissions follow the individual's Table-2 row.
        pass
    if cut is not None and base not in _CUT_BASES:
        _fail(descriptor, f"base {base!r} does not accept /C "
                          f"(MTB26 lists no Cut combo for it)")
    if median is not None and base not in _MEDIAN_BASES:
        _fail(descriptor, f"base {base!r} does not accept /M "
                          f"(MTB26 lists no Median combo for it)")
    if limit_halves and base != "KS":
        _fail(descriptor, f"only KS accepts /L (got base {base!r})")
    if sssc_k is not None:
        _fail(descriptor, f"only SSSC accepts /K (got base {base!r})")
    if forfeits_played and base not in ("DE", "BH", "SB", "FB"):
        _fail(descriptor, f"base {base!r} does not accept /P")
    if fore and base not in ("BH", "AOB"):
        _fail(descriptor, f"base {base!r} does not accept /F "
                          f"(use the FB base directly)")
    if reverse and base not in ("TPN", "RTNG"):
        _fail(descriptor, f"base {base!r} does not accept /R")


# ------------------------------------------------------------------
# Canonical criterion ids
# ------------------------------------------------------------------

#: Named (C1/C2/M1/M2) descriptor -> existing fide-2026 criterion id.
_NAMED_IDS: Dict[Tuple[str, str], str] = {
    ("BH", "C1"): "buchholz_cut1",
    ("BH", "C2"): "buchholz_cut2",
    ("BH", "M1"): "median_buchholz",
    ("BH", "M2"): "median_buchholz_2",
    ("SB", "C1"): "sonneborn_berger_cut1",
    ("SB", "C2"): "sonneborn_berger_cut2",
    ("PS", "C1"): "progressive_cut1",
    ("ARO", "C1"): "aro_cut1",
    ("ARO", "C2"): "aro_cut2",
    ("ARO", "M1"): "aro_median1",
    ("ARO", "M2"): "aro_median2",
    ("FB", "C1"): "fore_buchholz_cut1",
    ("FB", "C2"): "fore_buchholz_cut2",
    ("FB", "M1"): "fore_median1",
    ("FB", "M2"): "fore_median2",
}

_BASE_IDS: Dict[str, str] = {
    "BH": "buchholz",
    "SB": "sonneborn_berger",
    "PS": "progressive",
    "ARO": "aro",
    "FB": "fore_buchholz",
    "AOB": "aob",
    "KS": "koya",
}


def canonical_id(spec: ModifierSpec) -> str:
    """Map ``spec`` to the criterion id used in ``values`` dicts.

    Named combos reuse the existing fide-2026 ids; generic ``n``
    instantiations use synthetic ``<stem>_c<n>`` / ``<stem>_m<n>``
    ids (e.g. ``buchholz_c3``). Non-scalar stages (DE/TPN/RTNG)
    return their stage names.
    """
    if spec.is_team:
        raise UnsupportedCriterionError(
            f"{spec.base} (team descriptor; use tiebreak_core.team)",
            "fide-2026")
    base = spec.base
    if base in ("DE", "TPN", "RTNG"):
        return {"DE": "direct_encounter", "TPN": "tpn",
                "RTNG": "rtng"}[base]
    if spec.fore and base == "BH":
        base = "FB"
    if spec.fore and spec.base == "AOB":
        return "aob_fb"
    if spec.cut is not None:
        key = (base, f"C{spec.cut}")
        if key in _NAMED_IDS:
            return _NAMED_IDS[key]
        return f"{_BASE_IDS[base]}_c{spec.cut}"
    if spec.median is not None:
        key = (base, f"M{spec.median}")
        if key in _NAMED_IDS:
            return _NAMED_IDS[key]
        return f"{_BASE_IDS[base]}_m{spec.median}"
    if base == "KS" and spec.limit_halves:
        return "koya"
    return _BASE_IDS[base]


# ------------------------------------------------------------------
# Generic individual calculation (fide-2026)
# ------------------------------------------------------------------

def calculate_descriptor(player, all_players: Mapping,
                         descriptor: str, total_rounds: int,
                         mode: str = "swiss",
                         draw_points: float = 0.5) -> float:
    """Calculate one MTB26 descriptor value (individual scope).

    ``/P`` maps to the fide-2026 ``forfeits_as_played`` opt-in;
    ``/L±n`` maps to the §14.5 ``koya_limit`` (``n`` half-points).
    Team descriptors raise :class:`UnsupportedCriterionError`
    (use ``tiebreak_core.team``). Non-scalar stages (DE/TPN/RTNG)
    raise :class:`UnsupportedCriterionError` (use ranking).
    """
    from tiebreak_core import fide2026 as _f26

    spec = parse_descriptor(descriptor)
    if spec.is_team:
        raise UnsupportedCriterionError(
            f"{descriptor!r} (team descriptor; use tiebreak_core.team)",
            "fide-2026")
    if spec.base in ("DE", "TPN", "RTNG"):
        raise UnsupportedCriterionError(
            f"{descriptor!r} (ranking stage under fide-2026; "
            f"use rank_descriptors, not calculate)", "fide-2026")
    if spec.reverse:
        raise InvalidDescriptorError(
            descriptor, "/R is a ranking-direction modifier, not a value")
    if spec.base not in _BASE_IDS and not (
            spec.fore and spec.base in ("BH", "AOB")):
        raise UnsupportedCriterionError(descriptor, "fide-2026")
    if spec.base == "KS":
        return _f26.koya(player, dict(all_players), total_rounds, mode,
                         draw_points, spec.forfeits_played,
                         spec.limit_halves * 0.5)
    if spec.limit_halves:
        raise InvalidDescriptorError(descriptor, "unreachable")
    base = spec.base
    if spec.fore and base == "BH":
        base = "FB"
    if spec.fore and spec.base == "AOB":
        if spec.forfeits_played:
            return _aob_fb_generic(player, all_players, total_rounds,
                                   mode, draw_points,
                                   spec.forfeits_played)
        return _f26.average_opponents_fore_buchholz(
            player, dict(all_players), total_rounds, mode, draw_points,
            spec.forfeits_played)
    if spec.cut is not None:
        named = _NAMED_IDS.get((base, f"C{spec.cut}"))
        if named is not None:
            return _f26.FIDE2026_REGISTRY[named](
                player, dict(all_players), total_rounds, mode,
                draw_points, spec.forfeits_played)
        return _generic_cut(player, all_players, base, spec.cut,
                            total_rounds, mode, draw_points,
                            spec.forfeits_played)
    if spec.median is not None:
        named = _NAMED_IDS.get((base, f"M{spec.median}"))
        if named is not None:
            return _f26.FIDE2026_REGISTRY[named](
                player, dict(all_players), total_rounds, mode,
                draw_points, spec.forfeits_played)
        return _generic_median(player, all_players, base, spec.median,
                               total_rounds, mode, draw_points,
                               spec.forfeits_played)
    if base == "PS":
        return _f26.progressive(player, dict(all_players), total_rounds,
                                mode, draw_points,
                                spec.forfeits_played)
    func = _f26.FIDE2026_REGISTRY[_BASE_IDS[base]]
    return func(player, dict(all_players), total_rounds, mode,
                draw_points, spec.forfeits_played)


def _generic_cut(player, all_players: Mapping, base: str, n: int,
                 total_rounds: int, mode: str, draw_points: float,
                 forfeits_as_played: bool) -> float:
    """Arbitrary /Cn (n >= 3 for BH/SB/ARO/FB; n >= 2 for PS)."""
    from tiebreak_core import fide2024 as _f24
    from tiebreak_core import fide2026 as _f26

    shared = dict(all_players)
    if base == "PS":
        return _progressive_cut_n(player, shared, n, total_rounds, mode,
                                  draw_points)
    if base == "ARO":
        opps = sorted(o.rating for o in
                      _f26._otb_rated_opponents(player, shared))
        if not opps:
            return 0.0
        rest = opps[min(n, len(opps) - 1):]  # keep >= 1 (C2 guard shape)
        return float(_f24._fide_round_half_up(sum(rest) / len(rest)))
    pre = _f26._precompute(shared, total_rounds, mode, draw_points)
    ctx, adj = pre
    eff = _f26._regular_mode(mode, forfeits_as_played)
    if base == "BH":
        contribs = _f26._buchholz_contribs(
            player.points, ctx[player.player_id], adj, eff, draw_points,
            total_rounds)
        if len(contribs) < 2:
            return sum(c.value for c in contribs)
        return sum(c.value for c in _f24._apply_cuts_least(contribs, n))
    if base == "SB":
        elements = _f26._sb_scored(player.points,
                                   ctx[player.player_id], adj, eff,
                                   draw_points, total_rounds)
        if len(elements) < 2:
            return sum(e.value for e in elements)
        remaining = list(elements)
        for _ in range(min(n, len(remaining) - 1)):  # keep >= 1
            remaining.pop(_f26._sb_c1_victim_index(remaining))
        return sum(e.value for e in remaining)
    if base == "FB":
        own_fb, fb_adj = _f26._fb_tables(ctx, shared, total_rounds)
        contribs = _f26._fb_contribs(
            player, ctx, own_fb, fb_adj, mode, draw_points,
            total_rounds, forfeits_as_played)
        if len(contribs) < 2:
            return sum(c.value for c in contribs)
        return sum(c.value for c in _f24._apply_cuts_least(contribs, n))
    raise UnsupportedCriterionError(f"{base}/C{n}", "fide-2026")


def _generic_median(player, all_players: Mapping, base: str, n: int,
                    total_rounds: int, mode: str, draw_points: float,
                    forfeits_as_played: bool) -> float:
    """Arbitrary /Mn: drop n least (VUR-aware) then n most."""
    from tiebreak_core import fide2024 as _f24
    from tiebreak_core import fide2026 as _f26

    shared = dict(all_players)
    if base == "ARO":
        opps = sorted(o.rating for o in
                      _f26._otb_rated_opponents(player, shared))
        if len(opps) < 2 * n + 1:
            if not opps:
                return 0.0
            return float(_f24._fide_round_half_up(
                sum(opps) / len(opps)))
        rest = opps[n:-n] if n else opps
        return float(_f24._fide_round_half_up(sum(rest) / len(rest)))
    pre = _f26._precompute(shared, total_rounds, mode, draw_points)
    ctx, adj = pre
    eff = _f26._regular_mode(mode, forfeits_as_played)
    if base == "BH":
        contribs = _f26._buchholz_contribs(
            player.points, ctx[player.player_id], adj, eff, draw_points,
            total_rounds)
    elif base == "FB":
        own_fb, fb_adj = _f26._fb_tables(ctx, shared, total_rounds)
        contribs = _f26._fb_contribs(
            player, ctx, own_fb, fb_adj, mode, draw_points,
            total_rounds, forfeits_as_played)
    else:
        raise UnsupportedCriterionError(f"{base}/M{n}", "fide-2026")
    if len(contribs) < 2 * n + 1:
        return sum(c.value for c in contribs)
    rest = _f24._apply_cuts_least(contribs, n)
    for _ in range(n):
        rest = _f24._remove_max(rest)
    return sum(c.value for c in rest)


def _progressive_cut_n(player, shared: Mapping, n: int,
                       total_rounds: int, mode: str,
                       draw_points: float) -> float:
    """PS/Cn: exclude cumulative scores after rounds 1..n.

    Generalizes §14.1.1.c (PS-C1) per the MTB26 generic machine:
    each excluded round removes that round's cumulative standing
    from the progressive sum.
    """
    from tiebreak_core import fide2026 as _f26

    pre = _f26._precompute(shared, total_rounds, mode, draw_points)
    ctx, _ = pre
    by_round: Dict[int, float] = {}
    for r in ctx[player.player_id]:
        by_round[r.round_number] = by_round.get(r.round_number, 0.0) + r.score
    cumulative, total = 0.0, 0.0
    excluded = 0.0
    for rnd in range(1, total_rounds + 1):
        cumulative += by_round.get(rnd, 0.0)
        total += cumulative
        if rnd <= n:
            excluded += cumulative
    return total - excluded


def _aob_fb_generic(player, all_players: Mapping, total_rounds: int,
                    mode: str, draw_points: float,
                    forfeits_as_played: bool) -> float:
    """AOB/F with explicit /P routing (same projection, flag carried)."""
    from tiebreak_core import fide2026 as _f26

    return _f26.average_opponents_fore_buchholz(
        player, dict(all_players), total_rounds, mode, draw_points,
        forfeits_as_played)


# ------------------------------------------------------------------
# Descriptor ranking (individual scope, fide-2026)
# ------------------------------------------------------------------

def rank_descriptors(players: Mapping, descriptors: Sequence[str],
                     total_rounds: int,
                     deterministic_keys: Mapping | None = None,
                     mode: str = "swiss",
                     draw_points: float = 0.5,
                     pairing_numbers: Mapping | None = None
                     ):
    """Rank standings by an ordered MTB26 descriptor list.

    Semantics mirror ``fide2026.rank_standings`` stage-for-stage;
    ``/P`` enables forfeit inclusion, ``/L±n`` sets the Koya limit,
    ``/R`` reverses the terminal direction (TPN/R sorts pairing
    numbers descending; RTNG/R sorts ratings ascending).
    Team descriptors raise :class:`UnsupportedCriterionError`.
    """
    from tiebreak_core import fide2024 as _f24
    from tiebreak_core import fide2026 as _f26
    from tiebreak_core.models import PlayerResult, StandingsResult

    specs = [parse_descriptor(d) for d in descriptors]
    for spec, raw in zip(specs, descriptors):
        if spec.is_team:
            raise UnsupportedCriterionError(
                f"{raw!r} (team descriptor; use tiebreak_core.team)",
                "fide-2026")
    shared = dict(players)
    _f26._precompute(shared, total_rounds, mode, draw_points)
    keys = deterministic_keys or {}
    tpn = _f26._validate_pairing_numbers(pairing_numbers, shared) \
        if any(s.base == "TPN" for s in specs) else {}
    ordered_ids = sorted(shared, key=lambda pid: keys.get(pid, pid))
    scalar_ids: List[str] = []
    values: Dict[int, Dict[str, float]] = {pid: {} for pid in ordered_ids}
    for spec, raw in zip(specs, descriptors):
        if spec.base in ("DE", "TPN", "RTNG"):
            continue
        cid = canonical_id(spec)
        scalar_ids.append(cid)
        for pid in ordered_ids:
            values[pid][cid] = calculate_descriptor(
                shared[pid], shared, raw, total_rounds, mode,
                draw_points)
    # Koya-limit scope check mirrors fide2026.rank_standings.
    for spec, raw in zip(specs, descriptors):
        if spec.limit_halves and spec.base != "KS":
            raise InvalidDescriptorError(raw, "unreachable")
    groups: List[List[int]] = _f24._split_by(
        [ordered_ids], lambda pid: -(shared[pid].points or 0.0))
    for spec, raw in zip(specs, descriptors):
        cid = canonical_id(spec) if spec.base not in (
            "DE", "TPN", "RTNG") else None
        if spec.base == "DE":
            eff = _f26._regular_mode(
                mode, spec.forfeits_played)
            groups = [tier for g in groups
                      for tier in _f26._de_tiers(g, shared, eff)]
        elif spec.base == "TPN":
            keyfun = (lambda pid: -tpn[pid]) if spec.reverse \
                else (lambda pid: tpn[pid])
            groups = _f24._split_by(groups, keyfun)
        elif spec.base == "RTNG":
            keyfun = (lambda pid: (shared[pid].rating or 0)) \
                if spec.reverse \
                else (lambda pid: -(shared[pid].rating or 0))
            groups = _f24._split_by(groups, keyfun)
        else:
            assert cid is not None
            groups = _f24._split_by(
                groups, lambda pid, _c=cid: -values[pid][_c])
    flat = [pid for g in groups for pid in g]
    ranked = tuple(
        PlayerResult(player_id=pid, points=shared[pid].points or 0.0,
                     values=dict(values[pid]), rank=i + 1)
        for i, pid in enumerate(flat))
    return StandingsResult(players=ranked, criteria=tuple(descriptors),
                           rules_version="fide-2026")


__all__ = [
    "ModifierSpec",
    "parse_descriptor",
    "canonical_id",
    "calculate_descriptor",
    "rank_descriptors",
]
