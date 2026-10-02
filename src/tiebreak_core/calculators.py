"""
Tiebreak calculators.
Pure Python - no Flask, no DB.
Each function is independent and testable.

v0.1.0: behavior-preserving extraction from chess-manager
``domain/tiebreak/calculators.py``. Algorithm bodies are UNCHANGED
(rounding, virtual-opponent handling, cut rules, dp table). Only the
import path changed. See docs/KNOWN_LIMITATIONS.md for documented
divergences from FIDE C.07 (NOT fixed here by design).
"""
from typing import Dict, List
from tiebreak_core.models import PlayerTiebreakData


# ------------------------------------------------------------------
# Individual calculators
# ------------------------------------------------------------------

def buchholz(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Sum of opponents' scores (including Virtual Opponent handling)."""
    total = 0.0
    for game in player.games:
        if game.opponent_id == -1:
            # FIDE Rule C.02.13.1: محاسبات حریف مجازی برای بازی‌های انجام‌نشده
            # به صورت تقریبی و استاندارد، امتیاز خود بازیکن لحاظ می‌شود 
            # (منهای امتیازی که در این بازی گرفته است).
            total += max(0.0, player.points - game.score)
        elif game.opponent_id in all_players:
            total += all_players[game.opponent_id].points
    return round(total, 1)


def buchholz_cut1(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Buchholz minus lowest opponent score."""
    scores = []
    for game in player.games:
        if game.opponent_id == -1:
            scores.append(max(0.0, player.points - game.score))
        elif game.opponent_id in all_players:
            scores.append(all_players[game.opponent_id].points)
            
    if not scores:
        return 0.0
    
    total = sum(scores)
    if len(scores) > 1:
        total -= min(scores)
        
    return round(total, 1)


def buchholz_cut2(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Buchholz minus two lowest opponent scores."""
    scores = []
    for game in player.games:
        if game.opponent_id == -1:
            scores.append(max(0.0, player.points - game.score))
        elif game.opponent_id in all_players:
            scores.append(all_players[game.opponent_id].points)
            
    scores.sort()
    if not scores:
        return 0.0
        
    total = sum(scores)
    cuts = min(2, len(scores) - 1)
    for i in range(cuts):
        total -= scores[i]
        
    return round(total, 1)


def median_buchholz(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Buchholz minus highest and lowest."""
    scores = []
    for game in player.games:
        if game.opponent_id == -1:
            scores.append(max(0.0, player.points - game.score))
        elif game.opponent_id in all_players:
            scores.append(all_players[game.opponent_id].points)

    if len(scores) < 3:
        return buchholz(player, all_players)

    return round(sum(scores) - min(scores) - max(scores), 1)


def median_buchholz_2(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Buchholz minus two highest and two lowest (FIDE Median-2, BH-M2).

    Source: FIDE Handbook C.07 pre-2023 §4.3 ("Buchholz reduced by the two
    highest and the two lowest scores"), retained in later editions (§14).
    Edge policy (implementation choice, documented): with fewer than 5
    opponent scores the trim is undefined, so fall back to full Buchholz —
    mirroring the legacy Median fallback for <3 games.
    """
    scores = []
    for game in player.games:
        if game.opponent_id == -1:
            scores.append(max(0.0, player.points - game.score))
        elif game.opponent_id in all_players:
            scores.append(all_players[game.opponent_id].points)

    if len(scores) < 5:
        return buchholz(player, all_players)

    ordered = sorted(scores)
    return round(sum(ordered[2:-2]), 1)


def sonneborn_berger(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Sum of (opponent_points * score_against_opponent)."""
    total = 0.0
    for game in player.games:
        if game.opponent_id == -1:
            opp_points = max(0.0, player.points - game.score)
        elif game.opponent_id in all_players:
            opp_points = all_players[game.opponent_id].points
        else:
            continue
        total += opp_points * game.score
        
    return round(total, 2)


def progressive(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Cumulative score sum across rounds."""
    sorted_games = sorted(player.games, key=lambda g: g.round_number)
    cumulative = 0.0
    total = 0.0
    for game in sorted_games:
        cumulative += game.score
        total += cumulative
    return round(total, 1)


def wins_count(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    return float(player.wins)


def wins_with_black(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    return float(player.wins_with_black)


def games_with_black(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    return float(player.games_with_black)


def average_rating_opponents(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Average rating of opponents (ARO)."""
    ratings = []
    for game in player.games:
        if game.opponent_id == -1:
            # طبق قوانین FIDE، ریتینگ حریف مجازی برابر با ریتینگ خود بازیکن در نظر گرفته می‌شود
            if player.rating > 0:
                ratings.append(player.rating)
        elif game.opponent_id in all_players and all_players[game.opponent_id].rating > 0:
            ratings.append(all_players[game.opponent_id].rating)
            
    if not ratings:
        return 0.0
    return round(sum(ratings) / len(ratings))


def koya(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData],
    total_rounds: int
) -> float:
    """Score against players with >= 50% score."""
    if total_rounds == 0:
        return 0.0
        
    half = total_rounds / 2
    total = 0.0
    for game in player.games:
        if game.opponent_id == -1:
            opp_points = max(0.0, player.points - game.score)
        elif game.opponent_id in all_players:
            opp_points = all_players[game.opponent_id].points
        else:
            continue
            
        if opp_points >= half:
            total += game.score
            
    return round(total, 1)

def direct_encounter(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData],
    opponent_id: int = 0
) -> float:
    """Score in direct encounter against specific opponent."""
    for g in player.games:
        if g.opponent_id == opponent_id:
            return g.score
    return 0.0


def buchholz_sum(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Sum of Buchholz of opponents (Buchholz of Buchholz)."""
    total = 0.0
    for oid in player.opponent_ids:
        if oid in all_players:
            total += buchholz(all_players[oid], all_players)
    return round(total, 1)


def arpo(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """
    Average Rating of Performance of Opponents.
    For each opponent, calculate their performance rating,
    then average.
    """
    performances = []
    for oid in player.opponent_ids:
        opp = all_players.get(oid)
        if not opp or not opp.games:
            continue
        opp_total = sum(g.score for g in opp.games)
        opp_count = len(opp.games)
        if opp_count == 0:
            continue
        opp_ratings = [
            all_players[g.opponent_id].rating
            for g in opp.games
            if g.opponent_id in all_players and all_players[g.opponent_id].rating > 0
        ]
        if not opp_ratings:
            continue
        avg_opp_rating = sum(opp_ratings) / len(opp_ratings)
        percentage = opp_total / opp_count
        dp = _get_dp_for_arpo(percentage)
        perf = avg_opp_rating + dp
        performances.append(perf)

    if not performances:
        return 0.0
    return round(sum(performances) / len(performances))


def _get_dp_for_arpo(percentage: float) -> float:
    """Simplified dp lookup for ARPO."""
    dp_table = [
        (1.00, 800), (0.99, 677), (0.92, 401), (0.83, 273),
        (0.75, 193), (0.67, 125), (0.60, 72), (0.55, 36),
        (0.50, 0), (0.45, -36), (0.40, -72), (0.33, -125),
        (0.25, -193), (0.17, -273), (0.08, -401), (0.01, -677),
        (0.00, -800),
    ]
    for threshold, dp in dp_table:
        if percentage >= threshold:
            return dp
    return -800


# ------------------------------------------------------------------
# Registry and dispatcher
# ------------------------------------------------------------------

TIEBREAK_REGISTRY = {
    "buchholz": buchholz,
    "buchholz_cut1": buchholz_cut1,
    "buchholz_cut2": buchholz_cut2,
    "median_buchholz": median_buchholz,
    "median_buchholz_2": median_buchholz_2,
    "sonneborn_berger": sonneborn_berger,
    "progressive": progressive,
    "wins": wins_count,
    "wins_black": wins_with_black,
    "games_black": games_with_black,
    "aro": average_rating_opponents,
    "buchholz_sum": buchholz_sum,
    "arpo": arpo,
}

# NOTE: Persian display names live in tiebreak_core.display, NOT here.
# The calculation path must never depend on presentation metadata.


def calculate(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData],
    tiebreak: str,
    total_rounds: int = 0,
) -> float:
    """Calculate a single tie-break value (composable; no ranking)."""
    if tiebreak == "koya":
        return koya(player, all_players, total_rounds)
    if tiebreak == "direct_encounter":
        # Standings-level direct encounter is a no-op in legacy behavior.
        return 0.0
    func = TIEBREAK_REGISTRY.get(tiebreak)
    if func is None:
        return 0.0
    return func(player, all_players)


def calculate_all(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData],
    tiebreak_list: List[str],
    total_rounds: int = 0
) -> Dict[str, float]:
    """Calculate all requested tie-break values (no ranking applied)."""
    return {
        tb: calculate(player, all_players, tb, total_rounds)
        for tb in tiebreak_list
    }
