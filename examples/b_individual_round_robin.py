"""Example B — individual round robin (fide-2026 round_robin mode).

Koya is the round-robin home criterion (§9.2): points scored against
opponents finishing on >= 50% of the maximum possible score. In
round-robin mode, forfeit results count as regular games for
opposition sets (D12 carve-out: rating sets still exclude forfeits).
"""
from tiebreak_core import (
    GameRecord,
    PlayerTiebreakData,
    calculate_descriptor_strict,
    rank_descriptors_strict,
)

PLAYERS = {
    1: PlayerTiebreakData(1, 2000, 2.0, [
        GameRecord(2, 1900, 1.0, "white", 1, kind="played"),
        GameRecord(3, 1900, 1.0, "white", 2, kind="played"),
        GameRecord(4, 1900, 0.0, "white", 3, kind="played"),
    ]),
    2: PlayerTiebreakData(2, 1900, 1.0, [
        GameRecord(1, 2000, 0.0, "black", 1, kind="played"),
        GameRecord(4, 1900, 1.0, "white", 2, kind="played"),
        GameRecord(3, 1900, 0.0, "black", 3, kind="played"),
    ]),
    3: PlayerTiebreakData(3, 1900, 0.0, [
        GameRecord(4, 1900, 0.0, "black", 1, kind="played"),
        GameRecord(1, 2000, 0.0, "black", 2, kind="played"),
        GameRecord(2, 1900, 0.0, "black", 3, kind="played"),
    ]),
    4: PlayerTiebreakData(4, 1900, 2.0, [
        GameRecord(3, 1900, 1.0, "white", 1, kind="played"),
        GameRecord(2, 1900, 0.0, "black", 2, kind="played"),
        GameRecord(1, 2000, 1.0, "black", 3, kind="played"),
    ]),
}


def main() -> None:
    # Maximum possible = 3 rounds -> threshold 1.5. Player 1 beat
    # player 2 (1.0 < 1.5: no) and player 3 (0.0: no) -> Koya 0.0;
    # player 4 beat player 3 (0.0: no) and player 1 (2.0: yes 1.0).
    koya_1 = calculate_descriptor_strict(
        PLAYERS[1], PLAYERS, "KS", total_rounds=3, ruleset="fide-2026",
        mode="round_robin")
    koya_4 = calculate_descriptor_strict(
        PLAYERS[4], PLAYERS, "KS", total_rounds=3, ruleset="fide-2026",
        mode="round_robin")
    print("Koya P1:", koya_1, "P4:", koya_4)
    assert (koya_1, koya_4) == (0.0, 1.0)

    standings = rank_descriptors_strict(
        PLAYERS, ["KS", "BH/C1"], total_rounds=3, ruleset="fide-2026",
        mode="round_robin")
    print("ranking:", [p.player_id for p in standings.players])


if __name__ == "__main__":
    main()
