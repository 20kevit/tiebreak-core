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
