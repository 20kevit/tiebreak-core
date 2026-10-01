"""Golden/conformance tests — old chess-manager behavior is the baseline.

``tests/data_goldens.json`` was captured from the ORIGINAL
``domain/tiebreak/calculators.calculate_all`` (see tools/capture script
in git history) across representative states: round-robin, byes /
virtual opponents / missing opponents / zero-game players, odd counts
with black wins. New code must reproduce every value exactly and must
reproduce the legacy ranking order (points -> criteria -> key).

Also includes a live old-vs-new comparison: if the chess-manager repo
is present, the ORIGINAL modules are loaded directly from source
(importlib, no Flask/DB imports — domain/tiebreak is pure) and compared
against tiebreak_core on the same fixtures. Any difference FAILS.
"""
import importlib.util
import json
import pathlib

import pytest

from tiebreak_core.calculators import calculate_all
from tiebreak_core.models import PlayerTiebreakData, GameRecord
from tiebreak_core.ranking import rank_standings

GOLDENS = json.loads(
    (pathlib.Path(__file__).parent / "data_goldens.json").read_text()
)

TOTAL_ROUNDS = {
    "four_player_rr_total3": 3,
    "byes_forfeits_edge_total4": 4,
    "odd_black_wins_total3": 3,
}

# Same fixtures as the capture script, rebuilt with tiebreak_core models.
# Game tuples: (opponent_id, score, color, round, opponent_rating)
_FIXTURES_RAW = {
    "four_player_rr_total3": {
        1: {"rating": 2000, "points": 2.5,
            "games": [(2, 1, "white", 1, 1500), (3, 0.5, "white", 2, 1500), (4, 1, "white", 3, 1500)]},
        2: {"rating": 1900, "points": 1.0,
            "games": [(1, 0, "white", 1, 1500), (3, 0.5, "white", 2, 1500), (4, 0.5, "white", 3, 1500)]},
        3: {"rating": 1800, "points": 1.5,
            "games": [(1, 0.5, "white", 1, 1500), (2, 0.5, "white", 2, 1500), (4, 0.5, "white", 3, 1500)]},
        4: {"rating": 1700, "points": 1.0,
            "games": [(1, 0, "white", 1, 1500), (2, 0.5, "white", 2, 1500), (3, 0.5, "white", 3, 1500)]},
    },
    "byes_forfeits_edge_total4": {
        11: {"rating": 1800, "points": 3.0,
             "games": [(-1, 1, "white", 1, 0), (12, 1, "white", 2, 1500), (13, 0.5, "white", 3, 1500), (-1, 0.5, "white", 4, 0)]},
        12: {"rating": 1600, "points": 1.5,
             "games": [(-1, 0, "white", 1, 0), (11, 0, "white", 2, 1500), (99, 1, "white", 3, 1500)]},
        13: {"rating": 0, "points": 0.5,
             "games": [(11, 0.5, "white", 3, 1500)]},
        14: {"rating": 1500, "points": 0.0, "games": []},
    },
    "odd_black_wins_total3": {
        21: {"rating": 2000, "points": 2.0,
             "games": [(22, 1, "black", 1, 1500), (23, 1, "white", 2, 1500)]},
        22: {"rating": 1900, "points": 0.0,
             "games": [(21, 0, "white", 1, 1500), (23, 0, "black", 2, 1500)]},
        23: {"rating": 1700, "points": 1.0,
             "games": [(-1, 1, "white", 1, 0), (21, 0, "white", 2, 1500), (22, 1, "white", 3, 1500)]},
    },
}


def _build(raw):
    out = {}
    for pid, spec in raw.items():
        out[pid] = PlayerTiebreakData(
            player_id=pid, rating=spec["rating"], points=spec["points"],
            games=[GameRecord(opponent_id=o, opponent_rating=r, score=s,
                              color=c, round_number=n)
                   for (o, s, c, n, r) in spec["games"]],
        )
    return out


def _load_old_calculators():
    """Load ORIGINAL chess-manager calculators directly from source.

    Returns None when the repo is not present (CI without checkout).
    domain/tiebreak is pure Python; no Flask/DB import occurs.
    """
    import sys
    import types
    for repo_root, calc_path in (
        ("/opt/projects/chess-manager/repo",
         "/opt/projects/chess-manager/repo/domain/tiebreak/calculators.py"),
        ("/app/repo", "/app/repo/domain/tiebreak/calculators.py"),
    ):
        try:
            models_path = calc_path.replace("calculators.py", "models.py")
            pathlib.Path(models_path).stat()
            # Provide the absolute import the legacy module expects:
            #   from domain.tiebreak.models import ...
            for name in ("domain", "domain.tiebreak"):
                if name not in sys.modules:
                    pkg = types.ModuleType(name)
                    pkg.__path__ = []  # mark as package
                    sys.modules[name] = pkg
            models_spec = importlib.util.spec_from_file_location(
                "domain.tiebreak.models", models_path)
            models_mod = importlib.util.module_from_spec(models_spec)
            sys.modules["domain.tiebreak.models"] = models_mod
            models_spec.loader.exec_module(models_mod)
            calc_spec = importlib.util.spec_from_file_location(
                "domain.tiebreak.calculators", calc_path)
            calc_mod = importlib.util.module_from_spec(calc_spec)
            sys.modules["domain.tiebreak.calculators"] = calc_mod
            calc_spec.loader.exec_module(calc_mod)
            return calc_mod, models_mod
        except FileNotFoundError:
            continue
    return None


class TestGoldenValues:
    @pytest.mark.parametrize("fixture", sorted(_FIXTURES_RAW))
    def test_values_match_captured_baseline(self, fixture):
        players = _build(_FIXTURES_RAW[fixture])
        total = TOTAL_ROUNDS[fixture]
        expected = GOLDENS["fixtures"][fixture]
        for pid, pdata in players.items():
            got = calculate_all(pdata, players, GOLDENS["criteria"], total)
            for crit in GOLDENS["criteria"]:
                assert got[crit] == pytest.approx(expected[str(pid)][crit]), (
                    f"{fixture} player {pid} criterion {crit}: "
                    f"got {got[crit]} expected {expected[str(pid)][crit]}"
                )


class TestGoldenRanking:
    def test_four_player_order_preserved(self):
        # Legacy ranking: points DESC -> criteria DESC -> key ASC.
        players = _build(_FIXTURES_RAW["four_player_rr_total3"])
        criteria = ["buchholz_cut1", "buchholz", "sonneborn_berger", "progressive"]
        res = rank_standings(players, criteria, total_rounds=3,
                             deterministic_keys={1: 1, 2: 2, 3: 3, 4: 4})
        assert [p.player_id for p in res.players] == [1, 3, 2, 4]

    def test_edge_fixture_order_preserved(self):
        players = _build(_FIXTURES_RAW["byes_forfeits_edge_total4"])
        criteria = ["buchholz_cut1", "buchholz", "sonneborn_berger", "progressive"]
        res = rank_standings(players, criteria, total_rounds=4,
                             deterministic_keys={11: 1, 12: 2, 13: 3, 14: 4})
        # Recompute legacy order independently from raw values.
        vals = {pid: calculate_all(p, players, criteria, 4)
                for pid, p in players.items()}
        legacy = sorted(players, key=lambda pid: (
            -(players[pid].points or 0.0),
            *[-vals[pid].get(c, 0) for c in criteria],
            {11: 1, 12: 2, 13: 3, 14: 4}[pid],
        ))
        assert [p.player_id for p in res.players] == legacy


class TestOldVsNewLive:
    """Direct old-vs-new comparison on identical inputs (if repo present)."""

    @pytest.mark.parametrize("fixture", sorted(_FIXTURES_RAW))
    def test_live_equivalence(self, fixture):
        loaded = _load_old_calculators()
        if loaded is None:
            pytest.skip("chess-manager repo not available")
        old_calc_mod, old_models = loaded
        raw = _FIXTURES_RAW[fixture]
        total = TOTAL_ROUNDS[fixture]
        old_players = {}
        for pid, spec in raw.items():
            old_players[pid] = old_models.PlayerTiebreakData(
                player_id=pid, rating=spec["rating"], points=spec["points"],
                games=[old_models.GameRecord(
                    opponent_id=o, opponent_rating=r, score=s,
                    color=c, round_number=n)
                    for (o, s, c, n, r) in spec["games"]],
            )
        new_players = _build(raw)
        for pid in raw:
            old_res = old_calc_mod.calculate_all(
                old_players[pid], old_players, GOLDENS["criteria"], total)
            new_res = calculate_all(
                new_players[pid], new_players, GOLDENS["criteria"], total)
            assert new_res == old_res, f"{fixture} pid={pid}"


class TestDeterminism:
    def test_repeated_calls_identical(self):
        players = _build(_FIXTURES_RAW["four_player_rr_total3"])
        crit = ["buchholz", "progressive", "aro"]
        first = {pid: calculate_all(p, players, crit, 3)
                 for pid, p in players.items()}
        for _ in range(25):
            again = {pid: calculate_all(p, players, crit, 3)
                     for pid, p in players.items()}
            assert again == first
        r1 = rank_standings(players, crit, 3, {1: 1, 2: 2, 3: 3, 4: 4})
        r2 = rank_standings(players, crit, 3, {1: 1, 2: 2, 3: 3, 4: 4})
        assert r1 == r2
