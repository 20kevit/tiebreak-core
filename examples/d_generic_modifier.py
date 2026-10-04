"""Example D — generic MTB26 modifier (fide-2026).

Any valid cut/median depth works, not just the named C1/C2/M1/M2 ids:
BH/C3 drops the three least-significant Buchholz elements (with the
§16.5 VUR exception reapplied per cut). n=1/2 delegate to the named
implementations, so equivalent descriptors always agree.
"""
from tiebreak_core import (
    GameRecord,
    PlayerTiebreakData,
    calculate_descriptor_strict,
    calculate_strict,
    parse_descriptor,
)

PLAYERS = {
    1: PlayerTiebreakData(1, 2000, 3.0, [
        GameRecord(2, 1900, 1.0, "white", 1, kind="played"),
        GameRecord(3, 1900, 1.0, "white", 2, kind="played"),
        GameRecord(4, 1900, 1.0, "white", 3, kind="played"),
        GameRecord(5, 1900, 0.0, "white", 4, kind="played"),
    ]),
    2: PlayerTiebreakData(2, 1900, 0.0, [
        GameRecord(1, 2000, 0.0, "black", 1, kind="played")]),
    3: PlayerTiebreakData(3, 1900, 0.0, [
        GameRecord(1, 2000, 0.0, "black", 2, kind="played")]),
    4: PlayerTiebreakData(4, 1900, 0.0, [
        GameRecord(1, 2000, 0.0, "black", 3, kind="played")]),
    5: PlayerTiebreakData(5, 1900, 1.0, [
        GameRecord(1, 2000, 1.0, "black", 4, kind="played")]),
}


def main() -> None:
    spec = parse_descriptor("BH/C3")
    print("parsed:", spec)
    assert (spec.base, spec.cut) == ("BH", 3)

    bh_c3 = calculate_descriptor_strict(
        PLAYERS[1], PLAYERS, "BH/C3", total_rounds=4,
        ruleset="fide-2026")
    print("BH/C3:", bh_c3)
    assert bh_c3 == 1.0  # elements 0,0,0,1 minus three least -> 1.0

    # n=1 delegates to the named id exactly.
    assert calculate_descriptor_strict(
        PLAYERS[1], PLAYERS, "BH/C1", total_rounds=4,
        ruleset="fide-2026") == calculate_strict(
            PLAYERS[1], PLAYERS, "buchholz_cut1", total_rounds=4,
            ruleset="fide-2026")


if __name__ == "__main__":
    main()
