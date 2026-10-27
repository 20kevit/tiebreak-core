"""Differential probe — runs against tiebreak-core v1.2.0 and the candidate.

Executed inside each isolated environment by ``run_differential.py``.
Emits a canonical JSON object mapping a case tag to either a numeric
value or a ``Type: message`` error string.

Every call is wrapped so that a *signature* difference (e.g. the
candidate's added ``ruleset`` parameter on ``calculate_descriptor_strict``)
is recorded as an error string rather than aborting the run.  The driver
classifies those separately from genuine value changes.
"""

import json
import math
import sys


def _norm(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        return round(value, 6)
    if isinstance(value, (list, tuple)):
        return [_norm(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _norm(v) for k, v in value.items()}
    return value


def _call(fn, *args, **kwargs):
    try:
        return {"status": "ok", "value": _norm(fn(*args, **kwargs))}
    except Exception as exc:  # noqa: BLE001 - the point is to record it
        return {"status": "error",
                "error": f"{type(exc).__name__}: {exc}"}


def _fixture_individual():
    """Coherent Swiss fixture: points == sum of recorded round scores."""
    from tiebreak_core import GameRecord as G
    from tiebreak_core import PlayerTiebreakData as P
    return {
        1: P(1, 2000, 2.0, [
            G(2, 1900, 1.0, "white", 1, "played"),
            G(3, 1800, 1.0, "white", 2, "played")]),
        2: P(2, 1900, 0.0, [G(1, 2000, 0.0, "black", 1, "played")]),
        3: P(3, 1800, 0.0, [G(1, 2000, 0.0, "black", 2, "played")]),
    }


def _fixture_forfeit():
    """Swiss + a forfeit win/loss pair (Article 16 / ``/P`` territory).

    Coherent: P1 1.0+1.0=2.0, P2 0.0, P3 0.0.
    """
    from tiebreak_core import GameRecord as G
    from tiebreak_core import PlayerTiebreakData as P
    return {
        1: P(1, 2000, 2.0, [
            G(2, 1900, 1.0, "white", 1, "played"),
            G(3, 1800, 1.0, "white", 2, "forfeit_win",
              opponent_score=0.0)]),
        2: P(2, 1900, 0.0, [G(1, 2000, 0.0, "black", 1, "played")]),
        3: P(3, 1800, 0.0, [G(1, 2000, 0.0, "black", 2, "forfeit_loss")]),
    }


def _fixture_rr():
    """Round-robin with forfeit losses (REP scope, Article 15.2)."""
    from tiebreak_core import GameRecord as G
    from tiebreak_core import PlayerTiebreakData as P
    return {
        1: P(1, 2000, 2.0, [
            G(2, 1900, 1.0, "white", 1, "played"),
            G(3, 1800, 1.0, "white", 2, "played")]),
        2: P(2, 1900, 1.0, [
            G(1, 2000, 0.0, "black", 1, "played"),
            G(3, 1800, 1.0, "white", 2, "played")]),
        3: P(3, 1800, 0.0, [
            G(1, 2000, 0.0, "black", 1, "played"),
            G(2, 1900, 0.0, "black", 2, "played")]),
    }


def _fixture_rr_forfeit():
    """Round-robin with forfeit losses — the R2 REP discriminator."""
    from tiebreak_core import GameRecord as G
    from tiebreak_core import PlayerTiebreakData as P
    return {
        1: P(1, 2000, 3.0, [
            G(2, 1900, 1.0, "white", 1, "played"),
            G(3, 1800, 1.0, "white", 2, "played"),
            G(4, 1700, 1.0, "white", 3, "forfeit_win")]),
        2: P(2, 1900, 1.5, [
            G(1, 2000, 0.0, "black", 1, "played"),
            G(3, 1800, 0.5, "white", 2, "played"),
            G(4, 1700, 1.0, "white", 3, "forfeit_win")]),
        3: P(3, 1800, 1.5, [
            G(1, 2000, 0.0, "black", 1, "played"),
            G(2, 1900, 0.5, "black", 2, "played"),
            G(4, 1700, 1.0, "white", 3, "forfeit_win")]),
        4: P(4, 1700, 0.0, [
            G(1, 2000, 0.0, "black", 3, "forfeit_loss"),
            G(2, 1900, 0.0, "black", 3, "forfeit_loss"),
            G(3, 1800, 0.0, "black", 3, "forfeit_loss")]),
    }


def _fixture_team():
    from tiebreak_core.team import TeamFormat, TeamMatch, TeamRecord
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


NAMED_CRITERIA = (
    "buchholz", "buchholz_cut1", "buchholz_cut2", "median_buchholz",
    "median_buchholz_2", "sonneborn_berger", "sonneborn_berger_cut1",
    "sonneborn_berger_cut2", "progressive", "progressive_cut1",
    "wins", "won", "games_black", "wins_black", "rounds_elected",
    "std", "aro", "aro_cut1", "aro_cut2", "aro_median1", "aro_median2",
    "tpr", "ptp", "apro", "appo", "koya", "aob", "aob_fb",
    "fore_buchholz", "fore_buchholz_cut1", "fore_buchholz_cut2",
    "fore_median1", "fore_median2",
)

RULESETS = ("legacy-0.1.0", "fide-2024", "fide-2026")


def main():
    from tiebreak_core import __version__
    out = {"version": __version__, "cases": {}}

    def add(tag, fn, *args, **kwargs):
        out["cases"][tag] = _call(fn, *args, **kwargs)

    ind = _fixture_individual()
    forf = _fixture_forfeit()
    rr = _fixture_rr()
    rrf = _fixture_rr_forfeit()
    teams = _fixture_team()

    # --- version / ruleset inventory ---
    try:
        from tiebreak_core import rules as _rules
        out["rulesets"] = sorted(_rules.RULESETS)
    except Exception as exc:  # noqa: BLE001
        out["rulesets"] = f"{type(exc).__name__}: {exc}"

    # --- legacy-0.1.0 frozen arithmetic ---
    from tiebreak_core import calculators as _calc
    for crit in ("buchholz", "sonneborn_berger", "koya", "wins"):
        add(f"legacy.calculate.{crit}", _calc.calculate,
            ind[1], ind, crit, 2)

    # --- named criteria x ruleset (individual, Swiss) ---
    for ruleset in RULESETS:
        if ruleset == "legacy-0.1.0":
            continue
        for crit in NAMED_CRITERIA:
            add(f"named.{ruleset}.{crit}",
                _strict_calc(ruleset), ind[1], ind, crit, 2)

    # --- named criteria with the ``forfeits_as_played`` flag ---
    for ruleset in ("fide-2024", "fide-2026"):
        for crit in ("buchholz", "sonneborn_berger", "aob", "koya",
                     "fore_buchholz"):
            add(f"pflag.{ruleset}.{crit}",
                _strict_calc(ruleset, forfeits_as_played=True),
                forf[1], forf, crit, 2)

    # --- round-robin mode: the R2 REP discriminator ---
    for ruleset in ("fide-2024", "fide-2026"):
        for crit in ("rounds_elected", "buchholz", "koya", "sonneborn_berger"):
            add(f"rr.{ruleset}.{crit}",
                _strict_calc(ruleset, mode="round_robin"),
                rrf[1], rrf, crit, 3)
        add(f"rr.{ruleset}.rep_all_forfeit",
            _strict_all(ruleset, mode="round_robin"),
            rrf[1], rrf, ["rounds_elected"], 3)
        # P4 took three forfeit losses: the R2 §7.6 discriminator.
        add(f"rr.{ruleset}.rep_forfeit_loser",
            _strict_all(ruleset, mode="round_robin"),
            rrf[4], rrf, ["rounds_elected"], 3)

    # --- descriptors ---
    from tiebreak_core import calculate_descriptor_strict
    for ruleset in ("fide-2024", "fide-2026"):
        for desc in ("BH", "BH/C1", "BH/C2", "BH/M1", "SB", "SB/C1",
                     "SB/P", "KS", "AOB", "AOB/F", "FB", "FB/P",
                     "PS", "PS/C1", "WIN", "WON", "BPG", "BWG", "REP",
                     "STD", "TPN", "RTNG", "ARO", "TPR", "PTP", "APRO",
                     "APPO", "DE", "KS/L+1"):
            add(f"desc.{ruleset}.{desc}",
                calculate_descriptor_strict, ind[1], ind, desc, 2,
                ruleset=ruleset)

    # --- descriptors under round-robin (Article 8 scope) ---
    for desc in ("BH", "BH/C1", "AOB", "FB", "KS", "SB", "DE/P"):
        add(f"desc.rr.{desc}", calculate_descriptor_strict,
            ind[1], ind, desc, 2, ruleset="fide-2026",
            mode="round_robin")

    # --- ranking ---
    for ruleset in ("fide-2024", "fide-2026"):
        add(f"rank.{ruleset}", _rank_norm(ruleset), ind,
            ["buchholz", "sonneborn_berger"], 2)
    add("rank.rr", _rank_norm("fide-2026", mode="round_robin"), rrf,
        ["rounds_elected", "buchholz"], 3)

    # --- team criteria ---
    from tiebreak_core import calculate_team_strict
    for desc in ("MPvGP", "EMMSB", "EMGSB", "EGMSB", "EGGSB", "EDE",
                 "BC", "TBR", "BBE", "SSSC", "KS:MP", "WIN:MP", "PS:MP",
                 "BH:MP", "BH:GP", "FB:MP", "AOB:MP", "AOB:MP/F"):
        add(f"team.{desc}", calculate_team_strict, teams[1], teams,
            desc, 2)
    add("team.rank", _team_rank_norm(), teams,
        ["MPvGP", "EMMSB", "EDE"], 2)

    print(json.dumps(out, sort_keys=True))


_STRICT = {}


def _strict_calc(ruleset, **kwargs):
    from tiebreak_core import calculate_strict

    def fn(player, players, criterion, total_rounds):
        return calculate_strict(player, players, criterion, total_rounds,
                                ruleset=ruleset, **kwargs)
    return fn


def _rank_norm(ruleset, **kwargs):
    from tiebreak_core import rank_standings_strict

    def fn(players, descriptors, total_rounds):
        res = rank_standings_strict(players, list(descriptors),
                                    total_rounds, ruleset=ruleset, **kwargs)
        return [p.player_id for p in res.players]
    return fn


def _team_rank_norm():
    from tiebreak_core import rank_teams_strict

    def fn(teams, descriptors, total_rounds):
        res = rank_teams_strict(teams, list(descriptors), total_rounds)
        return [t.team_id for t in res.teams]
    return fn


def _strict_all(ruleset, **kwargs):
    from tiebreak_core import calculate_all_strict

    def fn(player, players, criteria, total_rounds):
        return calculate_all_strict(player, players, criteria,
                                    total_rounds, ruleset=ruleset, **kwargs)
    return fn


if __name__ == "__main__":
    main()
