"""Release gate: every examples/*.py script executes cleanly.

Each example carries its own assertions; this test additionally fails
if any example raises, so README-linked behavior cannot rot silently.
"""
import runpy
from pathlib import Path

import pytest

EXAMPLES = sorted(
    (Path(__file__).resolve().parent.parent / "examples").glob("*.py"))


def test_examples_directory_populated():
    names = {p.stem for p in EXAMPLES}
    assert {
        "a_individual_swiss",
        "b_individual_round_robin",
        "c_team_tournament",
        "d_generic_modifier",
        "e_invalid_modifier",
        "f_article16_policy",
        "g_deterministic_ranking",
    } <= names


@pytest.mark.parametrize(
    "script", [p.stem for p in EXAMPLES], ids=lambda s: s)
def test_example_executes(script):
    path = (Path(__file__).resolve().parent.parent / "examples"
            / f"{script}.py")
    runpy.run_path(str(path), run_name="__main__")
