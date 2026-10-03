"""
Strict additive API for tiebreak-core (Phase 0).

Same calculations as the legacy path, plus a fail-fast validation
boundary. Values produced here are IDENTICAL to the legacy path for
identical inputs under ``ruleset="legacy-0.1.0"`` (delegation, not
reimplementation); only malformed inputs and unknown criteria/rulesets
behave differently (typed errors instead of silent ``0.0``).

What is validated (core needs only — no tournament-management rules):
  - criterion ids resolve (else ``UnknownCriterionError``)
  - ruleset is supported (else ``UnsupportedRulesetError``;
    ``"fide-2026"`` is specified but NOT implemented (Phase F26-1)
  - scores are 0 / 0.5 / 1 (else ``InvalidGameRecordError``)
  - colors are "white" / "black" (else ``InvalidGameRecordError``)
  - round numbers are ints >= 0 (else ``InvalidGameRecordError``)
  - ratings are ints >= 0, points are finite numbers >= 0
  - players-mapping keys match ``player_id`` (else ``InvalidPlayerDataError``)

Rounding, virtual-opponent handling and ranking semantics are the frozen
legacy ones. See ``docs/KNOWN_LIMITATIONS.md``.
"""
from __future__ import annotations

import math
from typing import Dict, List, Mapping, Sequence

from tiebreak_core import calculators as _calc
from tiebreak_core.models import PlayerTiebreakData, StandingsResult
from tiebreak_core.ranking import order_ids as _order_ids
from tiebreak_core.ranking import rank_standings as _rank_standings
from tiebreak_core.registry import is_known
from tiebreak_core.rules import SUPPORTED_RULESETS
from tiebreak_core.errors import (
    DuplicatePlayerIdError,
    InvalidGameRecordError,
    InvalidPlayerDataError,
    UnknownCriterionError,
    UnsupportedRulesetError,
)

VALID_SCORES = (0.0, 0.5, 1.0)
VALID_COLORS = ("white", "black")


def require_ruleset(ruleset: str) -> str:
    """Validate explicit ruleset selection (no silent default drift)."""
    if ruleset not in SUPPORTED_RULESETS:
        raise UnsupportedRulesetError(ruleset, SUPPORTED_RULESETS)
    return ruleset


def require_criteria(criteria: Sequence[str]) -> List[str]:
    """Fail fast on unknown criterion ids (legacy path yields 0.0)."""
    checked = list(criteria)
    for criterion in checked:
        if not is_known(criterion):
            raise UnknownCriterionError(criterion)
    return checked


def validate_game(game: object, *, index: int = -1) -> None:
    """Validate one GameRecord. Raises InvalidGameRecordError."""
    from tiebreak_core.models import GameRecord

    if not isinstance(game, GameRecord):
        raise InvalidGameRecordError(
            f"game[{index}]: expected GameRecord, got {type(game).__name__}"
        )
    if isinstance(game.opponent_id, bool) or not isinstance(game.opponent_id, int):
        raise InvalidGameRecordError(
            f"game[{index}]: opponent_id must be int, got {game.opponent_id!r}"
        )
    if (
        isinstance(game.opponent_rating, bool)
        or not isinstance(game.opponent_rating, int)
        or game.opponent_rating < 0
    ):
        raise InvalidGameRecordError(
            f"game[{index}]: opponent_rating must be int >= 0, "
            f"got {game.opponent_rating!r}"
        )
    if (
        isinstance(game.score, bool)
        or not isinstance(game.score, (int, float))
        or not math.isfinite(game.score)
        or float(game.score) not in VALID_SCORES
    ):
        raise InvalidGameRecordError(
            f"game[{index}]: score must be one of {list(VALID_SCORES)}, "
            f"got {game.score!r}"
        )
    if game.color not in VALID_COLORS:
        raise InvalidGameRecordError(
            f"game[{index}]: color must be one of {list(VALID_COLORS)}, "
            f"got {game.color!r}"
        )
    if (
        isinstance(game.round_number, bool)
        or not isinstance(game.round_number, int)
        or game.round_number < 0
    ):
        raise InvalidGameRecordError(
            f"game[{index}]: round_number must be int >= 0, "
            f"got {game.round_number!r}"
        )
    _validate_kind(game, index)


def _validate_kind(game: object, index: int) -> None:
    """Validate game-kind vocabulary + kind/opponent consistency.

    Only what is checkable without tournament context: an explicitly
    played game needs a real opponent; bye-like kinds need the virtual
    sentinel; forfeit results may carry a scheduled (real) opponent or
    the sentinel when the pairing is unknown. Color is NOT constrained:
    adapters record the side sat (or would-have-sat) for unplayed games.
    """
    from tiebreak_core.models import GAME_KINDS, PLAYED, VIRTUAL_KINDS

    kind = game.kind
    if not isinstance(kind, str) or (kind and kind not in GAME_KINDS):
        raise InvalidGameRecordError(
            f"game[{index}]: kind must be one of {list(GAME_KINDS)} "
            f"(or empty for unspecified), got {kind!r}"
        )
    if not kind:
        return
    if kind == PLAYED and game.opponent_id == -1:
        raise InvalidGameRecordError(
            f"game[{index}]: kind 'played' requires a real opponent, "
            f"got opponent_id=-1"
        )
    if kind in VIRTUAL_KINDS and game.opponent_id != -1:
        raise InvalidGameRecordError(
            f"game[{index}]: kind {kind!r} requires opponent_id=-1, "
            f"got {game.opponent_id!r}"
        )


def validate_player(player: object) -> None:
    """Validate one PlayerTiebreakData. Raises InvalidPlayerDataError."""
    if not isinstance(player, PlayerTiebreakData):
        raise InvalidPlayerDataError(
            f"expected PlayerTiebreakData, got {type(player).__name__}"
        )
    if isinstance(player.player_id, bool) or not isinstance(player.player_id, int):
        raise InvalidPlayerDataError(
            f"player_id must be int, got {player.player_id!r}"
        )
    if (
        isinstance(player.rating, bool)
        or not isinstance(player.rating, int)
        or player.rating < 0
    ):
        raise InvalidPlayerDataError(
            f"player {player.player_id}: rating must be int >= 0, "
            f"got {player.rating!r}"
        )
    if (
        isinstance(player.points, bool)
        or not isinstance(player.points, (int, float))
        or not math.isfinite(player.points)
        or player.points < 0
    ):
        raise InvalidPlayerDataError(
            f"player {player.player_id}: points must be a finite number >= 0, "
            f"got {player.points!r}"
        )
    if not isinstance(player.games, list):
        raise InvalidPlayerDataError(
            f"player {player.player_id}: games must be a list"
        )
    try:
        for i, game in enumerate(player.games):
            validate_game(game, index=i)
    except InvalidGameRecordError as exc:
        raise InvalidPlayerDataError(
            f"player {player.player_id}: {exc}"
        ) from exc


def validate_players(
    players: Mapping[int, PlayerTiebreakData],
) -> Dict[int, PlayerTiebreakData]:
    """Validate a players mapping; returns a plain-dict copy.

    Mapping keys must match each value's ``player_id`` (mismatches are a
    classic silent-misranking source). Duplicate ids cannot occur in a
    mapping by construction; list-shaped inputs are rejected so that
    duplicates cannot slip through either.
    """
    if not isinstance(players, Mapping):
        raise InvalidPlayerDataError(
            f"players must be a mapping of id -> PlayerTiebreakData, "
            f"got {type(players).__name__}"
        )
    checked: Dict[int, PlayerTiebreakData] = {}
    for key, player in players.items():
        if isinstance(key, bool) or not isinstance(key, int):
            raise DuplicatePlayerIdError(f"player key must be int, got {key!r}")
        validate_player(player)
        if key != player.player_id:
            raise InvalidPlayerDataError(
                f"mapping key {key} != player.player_id {player.player_id}"
            )
        if key in checked:  # defensive; mappings cannot hold dupes
            raise DuplicatePlayerIdError(f"duplicate player id {key}")
        checked[key] = player
    return checked


def _require_total_rounds(total_rounds: int) -> None:
    if (
        isinstance(total_rounds, bool)
        or not isinstance(total_rounds, int)
        or total_rounds < 0
    ):
        raise InvalidPlayerDataError(
            f"total_rounds must be int >= 0, got {total_rounds!r}"
        )


def calculate_strict(
    player: PlayerTiebreakData,
    all_players: Mapping[int, PlayerTiebreakData],
    criterion: str,
    total_rounds: int = 0,
    ruleset: str = "legacy-0.1.0",
) -> float:
    """Validated single-criterion calculation.

    Under ``legacy-0.1.0`` values are identical to the legacy path
    (delegation). Under ``fide-2024`` the FIDE-2024 engine computes
    independently (see tiebreak_core.fide2024).
    """
    require_ruleset(ruleset)
    if ruleset == "fide-2024":
        from tiebreak_core import fide2024 as _fide
        _require_total_rounds(total_rounds)
        validate_player(player)
        players = validate_players(all_players)
        _fide.validate_inputs(players, total_rounds)
        return _fide.calculate(player, players, criterion, total_rounds)
    require_criteria([criterion])
    _require_total_rounds(total_rounds)
    validate_player(player)
    players = validate_players(all_players)
    return _calc.calculate(player, players, criterion, total_rounds)


def calculate_all_strict(
    player: PlayerTiebreakData,
    all_players: Mapping[int, PlayerTiebreakData],
    criteria: Sequence[str],
    total_rounds: int = 0,
    ruleset: str = "legacy-0.1.0",
) -> Dict[str, float]:
    """Validated multi-criterion calculation (ruleset-dispatched)."""
    require_ruleset(ruleset)
    if ruleset == "fide-2024":
        from tiebreak_core import fide2024 as _fide
        _require_total_rounds(total_rounds)
        validate_player(player)
        players = validate_players(all_players)
        _fide.validate_inputs(players, total_rounds)
        for criterion in criteria:
            _fide.require_supported(criterion)
        return _fide.calculate_all(player, players, list(criteria),
                                   total_rounds)
    checked_criteria = require_criteria(criteria)
    _require_total_rounds(total_rounds)
    validate_player(player)
    players = validate_players(all_players)
    return _calc.calculate_all(player, players, checked_criteria, total_rounds)


def rank_standings_strict(
    players: Mapping[int, PlayerTiebreakData],
    criteria: Sequence[str],
    total_rounds: int = 0,
    deterministic_keys: Mapping[int, int] | None = None,
    ruleset: str = "legacy-0.1.0",
) -> StandingsResult:
    """Validated ranking (ruleset-dispatched ordering)."""
    require_ruleset(ruleset)
    if ruleset == "fide-2024":
        from tiebreak_core import fide2024 as _fide
        _require_total_rounds(total_rounds)
        checked_players = validate_players(players)
        _fide.validate_inputs(checked_players, total_rounds)
        _fide.check_ranking_criteria(criteria)
        _validate_keys(deterministic_keys)
        return _fide.rank_standings(checked_players, list(criteria),
                                    total_rounds, deterministic_keys)
    checked_criteria = require_criteria(criteria)
    _require_total_rounds(total_rounds)
    checked_players = validate_players(players)
    _validate_keys(deterministic_keys)
    return _rank_standings(
        checked_players, checked_criteria, total_rounds, deterministic_keys
    )


def _validate_keys(
    deterministic_keys: Mapping[int, int] | None,
) -> None:
    if deterministic_keys is not None:
        if not isinstance(deterministic_keys, Mapping):
            raise InvalidPlayerDataError("deterministic_keys must be a mapping")
        for key, value in deterministic_keys.items():
            if (
                isinstance(key, bool)
                or not isinstance(key, int)
                or isinstance(value, bool)
                or not isinstance(value, int)
            ):
                raise InvalidPlayerDataError(
                    "deterministic_keys must map int -> int"
                )


def order_ids_strict(
    points: Mapping[int, float],
    values: Mapping[int, Mapping[str, float]],
    criteria: Sequence[str],
    deterministic_keys: Mapping[int, int] | None = None,
    ruleset: str = "legacy-0.1.0",
) -> List[int]:
    """Validated pure comparator (order identical to legacy ``order_ids``)."""
    require_ruleset(ruleset)
    checked_criteria = require_criteria(criteria)
    if not isinstance(points, Mapping):
        raise InvalidPlayerDataError("points must be a mapping")
    for pid, pts in points.items():
        if isinstance(pid, bool) or not isinstance(pid, int):
            raise InvalidPlayerDataError(f"point key must be int, got {pid!r}")
        if (
            isinstance(pts, bool)
            or not isinstance(pts, (int, float))
            or not math.isfinite(pts)
        ):
            raise InvalidPlayerDataError(
                f"points[{pid}] must be a finite number, got {pts!r}"
            )
    return _order_ids(points, values, checked_criteria, deterministic_keys)


__all__ = [
    "VALID_SCORES",
    "VALID_COLORS",
    "require_ruleset",
    "require_criteria",
    "validate_game",
    "validate_player",
    "validate_players",
    "calculate_strict",
    "calculate_all_strict",
    "rank_standings_strict",
    "order_ids_strict",
]
