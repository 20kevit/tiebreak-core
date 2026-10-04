"""Hot-path benchmarks with generous anti-blowup bounds.

Asserts correctness of the ranked output and a wall-clock bound loose
enough to never flake on slow/loaded machines (it guards against
accidental cubic blowups, not for performance records). Real numbers
are recorded in docs/PERFORMANCE.md; per-run timings print with -s.
"""
import random
import time

from tiebreak_core import rank_standings
from tiebreak_core.models import GameRecord, PlayerTiebreakData

CRITERIA = ["buchholz_cut1", "buchholz", "sonneborn_berger", "progressive"]


def _players(n, rounds=7, seed=42):
    rng = random.Random(seed)
    out = {}
    for pid in range(1, n + 1):
        games = [
            GameRecord(opponent_id=((pid + i) % n) + 1, opponent_rating=1500,
                       score=rng.choice([0.0, 0.5, 1.0]),
                       color="white" if i % 2 else "black",
                       round_number=(i % rounds) + 1)
            for i in range(rounds)
        ]
        out[pid] = PlayerTiebreakData(pid, 1500, 3.5, games)
    return out


def _run(n):
    players = _players(n)
    start = time.perf_counter()
    res = rank_standings(players, CRITERIA, 7,
                         deterministic_keys={p: p for p in players})
    elapsed = time.perf_counter() - start
    print(f"\nbenchmark n={n}: {elapsed:.3f}s")
    return res, elapsed


def test_benchmark_100():
    res, _ = _run(100)
    assert len(res.players) == 100
    assert [p.rank for p in res.players] == list(range(1, 101))


def test_benchmark_500():
    res, elapsed = _run(500)
    assert len(res.players) == 500
    assert elapsed < 30


def test_benchmark_2000():
    res, elapsed = _run(2000)
    assert len(res.players) == 2000
    assert [p.rank for p in res.players] == list(range(1, 2001))
    assert elapsed < 30


def _players_26(n, rounds=7, seed=42):
    """Kind-annotated Swiss event (fide-2026 strict gate needs kinds)."""
    rng = random.Random(seed)
    out = {}
    for pid in range(1, n + 1):
        games, pts = [], 0.0
        for i in range(rounds):
            roll = rng.random()
            opp = ((pid + i) % n) + 1
            color = "white" if i % 2 else "black"
            if roll < 0.85:
                s = rng.choice([0.0, 0.5, 1.0])
                games.append(GameRecord(opponent_id=opp, opponent_rating=1500,
                                        score=s, color=color,
                                        round_number=i + 1, kind="played"))
                pts += s
            elif roll < 0.93:
                games.append(GameRecord(opponent_id=-1, opponent_rating=0,
                                        score=1.0, color=color,
                                        round_number=i + 1,
                                        kind="pairing_bye"))
                pts += 1.0
            else:
                games.append(GameRecord(opponent_id=-1, opponent_rating=0,
                                        score=0.5, color=color,
                                        round_number=i + 1,
                                        kind="requested_bye"))
                pts += 0.5
        out[pid] = PlayerTiebreakData(pid, 1500, pts, games)
    return out


CRITERIA_26 = ["buchholz_cut1", "buchholz", "sonneborn_berger",
               "progressive", "direct_encounter", "rtng"]


def test_benchmark_2000_fide2026():
    from tiebreak_core import fide2026
    players = _players_26(2000)
    start = time.perf_counter()
    res = fide2026.rank_standings(players, CRITERIA_26, 7)
    elapsed = time.perf_counter() - start
    print(f"\nbenchmark fide-2026 n=2000: {elapsed:.3f}s")
    assert len(res.players) == 2000
    assert [p.rank for p in res.players] == list(range(1, 2001))
    assert res.rules_version == "fide-2026"
    assert elapsed < 60


def test_benchmark_2000_fide2024():
    from tiebreak_core import fide2024
    players = _players_26(2000)
    start = time.perf_counter()
    res = fide2024.rank_standings(
        players, ["buchholz_cut1", "buchholz", "sonneborn_berger",
                  "progressive", "direct_encounter", "aro"], 7)
    elapsed = time.perf_counter() - start
    print(f"\nbenchmark fide-2024 n=2000: {elapsed:.3f}s")
    assert len(res.players) == 2000
    assert [p.rank for p in res.players] == list(range(1, 2001))
    assert res.rules_version == "fide-2024"
    assert elapsed < 60
