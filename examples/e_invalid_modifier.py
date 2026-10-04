"""Example E — typed failure behavior.

Malformed descriptors, FIDE-undefined combinations, unknown criteria,
wrong rulesets, and malformed records all raise typed errors — never
silent fallback values on the strict path.
"""
from tiebreak_core import (
    GameRecord,
    InvalidDescriptorError,
    InvalidPlayerDataError,
    PlayerTiebreakData,
    UnknownCriterionError,
    UnsupportedCriterionError,
    UnsupportedRulesetError,
    calculate_descriptor_strict,
    calculate_strict,
    parse_descriptor,
)

PLAYER = PlayerTiebreakData(1, 2000, 1.0, [
    GameRecord(2, 1900, 1.0, "white", 1, kind="played")])
POOL = {
    1: PLAYER,
    2: PlayerTiebreakData(2, 1900, 0.0, [
        GameRecord(1, 2000, 0.0, "black", 1, kind="played")]),
}


def main() -> None:
    # 1. MTB26 lists no median combo for SB -> rejected at parse time.
    try:
        parse_descriptor("SB/M1")
    except InvalidDescriptorError as exc:
        print("1:", exc)

    # 2. Team reference scores only exist for Table-2 bases.
    try:
        calculate_descriptor_strict(PLAYER, POOL, "ARO:GP",
                                    total_rounds=1, ruleset="fide-2026")
    except InvalidDescriptorError as exc:
        print("2:", exc)

    # 3. Unknown criterion on the strict path.
    try:
        calculate_strict(PLAYER, POOL, "nope", 1)
    except UnknownCriterionError as exc:
        print("3:", exc)

    # 4. Unknown ruleset.
    try:
        calculate_strict(PLAYER, POOL, "buchholz", 1, ruleset="fide-2030")
    except UnsupportedRulesetError as exc:
        print("4:", exc)

    # 5. Terminal/group stages are ranking-only (no scalar value).
    try:
        calculate_descriptor_strict(PLAYER, POOL, "TPN", total_rounds=1,
                                    ruleset="fide-2026")
    except UnsupportedCriterionError as exc:
        print("5:", exc)

    # 6. Malformed record (impossible score) is rejected up front.
    bad = PlayerTiebreakData(1, 2000, 1.0, [
        GameRecord(2, 1900, 0.7, "white", 1, kind="played")])
    try:
        calculate_strict(bad, POOL, "buchholz", 1)
    except InvalidPlayerDataError as exc:
        print("6:", exc)


if __name__ == "__main__":
    main()
