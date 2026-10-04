"""Example A — individual Swiss tie-breaks (fide-2026).

A 4-player, 3-round Swiss. Computes Buchholz Cut-1 and Sonneborn-Berger
for one player, then ranks the event.
"""
from tiebreak_core import (
    GameRecord,
    PlayerTiebreakData,
    calculate_all_strict,
    rank_standings_strict,
)

PLAYERS = {
    1: PlayerTiebreakData(1, 2000, 2.5, [
        GameRecord(2, 1900, 1.0, "white", 1, kind="played"),
        GameRecord(3, 1950, 0.5, "black", 2, kind="played"),
        GameRecord(4, 1800, 1.0, "white", 3, kind="played"),
    ]),
    2: PlayerTiebreakData(2, 1900, 1.0, [
        GameRecord(1, 2000, 0.0, "black", 1, kind="played"),
        GameRecord(4, 1800, 1.0, "white", 2, kind="played"),
        GameRecord(3, 1950, 0.0, "black", 3, kind="played"),
    ]),
    3: PlayerTiebreakData(3, 1950, 2.0, [
        GameRecord(4, 1800, 1.0, "white", 1, kind="played"),
        GameRecord(1, 2000, 0.5, "white", 2, kind="played"),
        GameRecord(2, 1900, 0.5, "white", 3, kind="played"),
    ]),
    4: PlayerTiebreakData(4, 1800, 0.0, [
        GameRecord(3, 1950, 0.0, "black", 1, kind="played"),
        GameRecord(2, 1900, 0.0, "black", 2, kind="played"),
        GameRecord(1, 2000, 0.0, "black", 3, kind="played"),
    ]),
}

CRITERIA = ["buchholz_cut1", "sonneborn_berger"]


def main() -> None:
    values = calculate_all_strict(
        PLAYERS[1], PLAYERS, CRITERIA, total_rounds=3,
        ruleset="fide-2026")
    print("player 1:", values)
    assert values == {"buchholz_cut1": 3.0, "sonneborn_berger": 2.0}

    standings = rank_standings_strict(
        PLAYERS, CRITERIA, total_rounds=3, ruleset="fide-2026")
    order = [p.player_id for p in standings.players]
    print("ranking:", order)
    assert order == [1, 3, 2, 4]


if __name__ == "__main__":
    main()
