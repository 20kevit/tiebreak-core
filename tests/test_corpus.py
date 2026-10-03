"""FIDE conformance corpus runner.

Loads every ``tests/corpus/*.json`` file, schema-validates all cases,
executes VERIFIED/CROSS_CHECKED cases against the strict API, and skips
PENDING cases (reported, never silently passing).
"""
import json
import pathlib

import pytest

from tiebreak_core import calculate_all_strict
from tiebreak_core.models import (
    GAME_KINDS,
    GameRecord,
    PlayerTiebreakData,
)

CORPUS_DIR = pathlib.Path(__file__).parent / "corpus"

REQUIRED_FIELDS = {
    "id", "ruleset", "status", "source", "source_grade", "article", "notes",
}
EXECUTABLE_STATUSES = ("VERIFIED", "CROSS_CHECKED")
GRADES = ("PRIMARY", "SECONDARY", "UNVERIFIED")


def _load_cases():
    cases = []
    for path in sorted(CORPUS_DIR.glob("*.json")):
        doc = json.loads(path.read_text())
        assert isinstance(doc.get("version"), int), f"{path}: missing version"
        for case in doc.get("cases", []):
            case = dict(case)
            case["_file"] = path.name
            cases.append(case)
    return cases


def _build_players(spec):
    players = {}
    for pid, p in spec.items():
        players[int(pid)] = PlayerTiebreakData(
            player_id=int(pid), rating=p["rating"], points=p["points"],
            games=[GameRecord(opponent_id=g["opponent"],
                              opponent_rating=g.get("rating", 0),
                              score=g["score"], color=g["color"],
                              round_number=g["round"],
                              kind=g.get("kind", ""))
                   for g in p["games"]],
        )
    return players


ALL_CASES = _load_cases()


@pytest.mark.parametrize("case", ALL_CASES, ids=[c["id"] for c in ALL_CASES])
def test_corpus_case(case):
    missing = REQUIRED_FIELDS - set(case)
    assert not missing, f"{case['id']}: missing fields {missing}"
    assert case["status"] in EXECUTABLE_STATUSES + ("PENDING",), (
        f"{case['id']}: bad status {case['status']}")
    assert case["source_grade"] in GRADES
    if case["status"] == "PENDING":
        # PENDING cases may carry kind-annotated input examples: validate
        # the vocabulary (not values) so the taxonomy stays honest.
        for pid, p in (case.get("players") or {}).items():
            for g in p.get("games", []):
                assert g.get("kind", "") in GAME_KINDS + ("",), (
                    f"{case['id']}: unknown kind {g.get('kind')!r}")
        pytest.skip(f"PENDING: {case['id']} ({case['article']}) — "
                    f"not implemented under ruleset {case['ruleset']}")
    players = _build_players(case["players"])
    total = case.get("total_rounds", 0)
    # Only players listed in `expected` are asserted; the rest are
    # context (opponent scores/ratings).
    for pid in case["expected"]:
        pdata = players[int(pid)]
        got = calculate_all_strict(pdata, players, case["criteria"], total,
                                    ruleset=case["ruleset"])
        for crit, want in case["expected"][str(pid)].items():
            assert got[crit] == pytest.approx(want), (
                f"{case['id']} player {pid} {crit}: got {got[crit]} "
                f"expected {want} [{case['article']}]")
