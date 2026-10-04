"""Example G — deterministic ranking.

Ordering is a pure function of (points, criterion values in listed
order, explicit deterministic keys). Re-running with the same inputs
gives the same order; caller data is never mutated; ties that no
stage can split fall back to the explicit keys (default: player id).
"""
from tiebreak_core import (
    GameRecord,
    PlayerTiebreakData,
    rank_standings_strict,
)

PLAYERS = {
    10: PlayerTiebreakData(10, 1800, 2.0, [
        GameRecord(20, 1800, 1.0, "white", 1, kind="played"),
        GameRecord(30, 1800, 1.0, "white", 2, kind="played"),
    ]),
    20: PlayerTiebreakData(20, 1800, 1.0, [
        GameRecord(10, 1800, 0.0, "black", 1, kind="played"),
        GameRecord(30, 1800, 1.0, "white", 2, kind="played"),
    ]),
    30: PlayerTiebreakData(30, 1800, 0.0, [
        GameRecord(10, 1800, 0.0, "black", 2, kind="played"),
        GameRecord(20, 1800, 0.0, "black", 2, kind="played"),
    ]),
}


def main() -> None:
    first = rank_standings_strict(
        PLAYERS, ["buchholz"], total_rounds=2, ruleset="fide-2026")
    second = rank_standings_strict(
        PLAYERS, ["buchholz"], total_rounds=2, ruleset="fide-2026")
    assert first == second  # deterministic
    order = [p.player_id for p in first.players]
    print("ranking:", order)
    assert order == [10, 20, 30]
    # Input records are untouched by ranking.
    assert PLAYERS[10].games[0].score == 1.0


if __name__ == "__main__":
    main()
