"""Example C — team tournament (C.07 §§11–13).

Four teams, single round robin, 4 boards, standard 2/1/0 match points.
Ranks by Extended Sonneborn-Berger (EMMSB), then Extended Direct
Encounter, then Board Count (lower wins).
"""
from tiebreak_core import (
    TeamFormat,
    TeamMatch,
    TeamRecord,
    calculate_team_strict,
    rank_teams_strict,
)

FMT = TeamFormat(mp_win=2.0, mp_draw=1.0)

TEAMS = {
    1: TeamRecord(1, 5.0, 9.5, [
        TeamMatch(2, 1, 2, 3.0), TeamMatch(3, 2, 2, 3.5),
        TeamMatch(4, 3, 1, 3.0)], (3.5, 2.5, 2.0, 1.5)),
    2: TeamRecord(2, 3.0, 7.0, [
        TeamMatch(1, 1, 0, 1.0), TeamMatch(4, 2, 2, 3.0),
        TeamMatch(3, 3, 1, 3.0)], (2.5, 2.0, 1.5, 1.0)),
    3: TeamRecord(3, 2.0, 6.0, [
        TeamMatch(4, 1, 1, 2.0), TeamMatch(1, 2, 0, 0.5),
        TeamMatch(2, 3, 1, 3.5)], (2.0, 1.5, 1.5, 1.0)),
    4: TeamRecord(4, 1.0, 4.5, [
        TeamMatch(3, 1, 1, 2.0), TeamMatch(2, 2, 0, 1.0),
        TeamMatch(1, 3, 0, 1.5)], (1.5, 1.0, 1.0, 1.5)),
}


def main() -> None:
    # EMMSB for team 1: 2*3.0 + 2*2.0 + 1*1.0 = 11.0
    emmsb = calculate_team_strict(TEAMS[1], TEAMS, "EMMSB",
                                  total_rounds=3, fmt=FMT)
    print("team 1 EMMSB:", emmsb)
    assert emmsb == 11.0

    standings = rank_teams_strict(TEAMS, ["EMMSB", "EDE", "BC"],
                                  total_rounds=3, fmt=FMT)
    order = [t.team_id for t in standings.teams]
    print("ranking:", order)
    assert order == [1, 2, 3, 4]


if __name__ == "__main__":
    main()
