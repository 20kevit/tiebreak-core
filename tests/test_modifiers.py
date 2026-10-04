"""Generic MTB26 modifier engine: parsing, validation, generics."""
import copy

import pytest

from tiebreak_core.errors import (
    InvalidDescriptorError,
    UnsupportedCriterionError,
)
from tiebreak_core import fide2026 as f26
from tiebreak_core.models import GameRecord, PlayerTiebreakData
from tiebreak_core.modifiers import (
    canonical_id,
    calculate_descriptor,
    parse_descriptor,
    rank_descriptors,
)


def _mk(pid, rating, pts, games):
    return PlayerTiebreakData(
        player_id=pid, rating=rating, points=pts,
        games=[GameRecord(opponent_id=o, opponent_rating=r, score=s,
                          color=c, round_number=n, kind=k)
               for (o, r, s, c, n, k) in games])


@pytest.fixture()
def swiss4():
    return {
        1: _mk(1, 2000, 3.5, [
            (2, 1900, 1.0, "white", 1, "played"),
            (3, 1950, 0.5, "black", 2, "played"),
            (4, 1800, 1.0, "white", 3, "played"),
            (2, 1900, 0.5, "black", 4, "played"),
            (3, 1950, 0.5, "white", 5, "played")]),
        2: _mk(2, 1900, 2.0, [
            (1, 2000, 0.0, "black", 1, "played"),
            (4, 1800, 1.0, "white", 2, "played"),
            (3, 1950, 0.5, "black", 3, "played"),
            (1, 2000, 0.5, "white", 4, "played"),
            (4, 1800, 0.0, "black", 5, "played")]),
        3: _mk(3, 1950, 2.5, [
            (4, 1800, 1.0, "white", 1, "played"),
            (1, 2000, 0.5, "white", 2, "played"),
            (2, 1900, 0.5, "white", 3, "played"),
            (4, 1800, 0.5, "black", 4, "played"),
            (1, 2000, 0.5, "black", 5, "played")]),
        4: _mk(4, 1800, 1.5, [
            (3, 1950, 0.0, "black", 1, "played"),
            (2, 1900, 0.0, "black", 2, "played"),
            (1, 2000, 0.0, "black", 3, "played"),
            (3, 1950, 0.5, "white", 4, "played"),
            (2, 1900, 1.0, "white", 5, "played")]),
    }


TR = 5


# ------------------------------------------------------------------
# Parsing: accepted descriptors
# ------------------------------------------------------------------

@pytest.mark.parametrize("descriptor,base,cut,median,limit,k,p,f,r,team", [
    ("BH", "BH", None, None, 0, None, False, False, False, None),
    ("bh/c1", "BH", 1, None, 0, None, False, False, False, None),
    ("BH/C12", "BH", 12, None, 0, None, False, False, False, None),
    ("ARO/M2", "ARO", None, 2, 0, None, False, False, False, None),
    ("KS/L+1", "KS", None, None, 1, None, False, False, False, None),
    ("KS/L-2", "KS", None, None, -2, None, False, False, False, None),
    ("KS/L3", "KS", None, None, 3, None, False, False, False, None),
    ("SB/C2/P", "SB", 2, None, 0, None, True, False, False, None),
    ("DE/P", "DE", None, None, 0, None, True, False, False, None),
    ("TPN/R", "TPN", None, None, 0, None, False, False, True, None),
    ("RTNG/R", "RTNG", None, None, 0, None, False, False, True, None),
    ("AOB/F", "AOB", None, None, 0, None, False, True, False, None),
    ("BH:GP/C1", "BH", 1, None, 0, None, False, False, False, "GP"),
    ("WIN:MP", "WIN", None, None, 0, None, False, False, False, "MP"),
    ("EMMSB/C1", "EMMSB", 1, None, 0, None, False, False, False, None),
    ("SSSC/K4", "SSSC", None, None, 0, 4, False, False, False, None),
    ("SSSC/F/P", "SSSC", None, None, 0, None, True, True, False, None),
    ("EDEBT/P", "EDEBT", None, None, 0, None, True, False, False, None),
    ("PS/C2", "PS", 2, None, 0, None, False, False, False, None),
])
def test_parse_accepted(descriptor, base, cut, median, limit, k, p, f, r,
                        team):
    spec = parse_descriptor(descriptor)
    assert spec.base == base
    assert spec.cut == cut
    assert spec.median == median
    assert spec.limit_halves == limit
    assert spec.sssc_k == k
    assert spec.forfeits_played == p
    assert spec.fore == f
    assert spec.reverse == r
    assert spec.team_score == team


# ------------------------------------------------------------------
# Parsing: rejected descriptors
# ------------------------------------------------------------------

@pytest.mark.parametrize("descriptor", [
    "SB/M1", "SB/M2",       # MTB26 lists no SB median combo
    "KS/P", "KS/C1",        # KS takes /L only
    "KS/R", "BH/R", "SB/R", "ARO/R",  # /R is TPN/RTNG-only
    "AOB/C1", "AOB/M1",     # AOB takes /F only
    "TPN/C1", "RTNG/M1",    # terminals take /R only
    "TPR/C1", "PTP/P",      # rating tables take no variants
    "BPG/C1", "REP/P",      # Type-B counts take no variants
    "STD/C1",               # STD takes no variants
    "BH/L+1", "ARO/L1",     # /L is KS-only
    "BH/K4",                # /K is SSSC-only
    "SSSC/L+1", "SSSC/R",   # SSSC takes /C /K /P /F
    "BC/C1", "TBR/P",       # knockout codes take no variants
    "EDE/C1",               # EDE takes /P only
    "SB:MP", "ARO:GP",      # team refs only on Table-2 bases
    "DE:MP", "TPN:GP",
    "XX", "OTHER_FOO", "", "BH/", "BH//C1", "/C1",
    "BH/C0", "BH/C65", "BH/M0", "KS/L0", "SSSC/K0",
    "BH/C01", "BH/M1/C1", "BH/C1/C2", "BH/P/P", "BH/M1/M2",
    "BH/X", "BH/C", "KS/L", "SSSC/K", "BH:XX", "BH:MP:GP",
])
def test_parse_rejected(descriptor):
    with pytest.raises(InvalidDescriptorError):
        parse_descriptor(descriptor)


# ------------------------------------------------------------------
# Canonical ids
# ------------------------------------------------------------------

@pytest.mark.parametrize("descriptor,expected", [
    ("BH", "buchholz"),
    ("BH/C1", "buchholz_cut1"),
    ("BH/C2", "buchholz_cut2"),
    ("BH/M1", "median_buchholz"),
    ("BH/M2", "median_buchholz_2"),
    ("BH/C3", "buchholz_c3"),
    ("BH/M3", "buchholz_m3"),
    ("SB/C1", "sonneborn_berger_cut1"),
    ("SB/C3", "sonneborn_berger_c3"),
    ("PS/C1", "progressive_cut1"),
    ("PS/C2", "progressive_c2"),
    ("ARO/M2", "aro_median2"),
    ("ARO/C5", "aro_c5"),
    ("FB/M1", "fore_median1"),
    ("AOB/F", "aob_fb"),
    ("KS/L+1", "koya"),
    ("DE", "direct_encounter"),
    ("TPN", "tpn"),
    ("RTNG", "rtng"),
])
def test_canonical_ids(descriptor, expected):
    assert canonical_id(parse_descriptor(descriptor)) == expected


# ------------------------------------------------------------------
# Named-combo equivalence (generic machine delegates at n=1,2)
# ------------------------------------------------------------------

_NAMED_PAIRS = [
    ("BH/C1", "buchholz_cut1"), ("BH/C2", "buchholz_cut2"),
    ("BH/M1", "median_buchholz"), ("BH/M2", "median_buchholz_2"),
    ("SB/C1", "sonneborn_berger_cut1"),
    ("SB/C2", "sonneborn_berger_cut2"),
    ("PS/C1", "progressive_cut1"),
    ("ARO/C1", "aro_cut1"), ("ARO/C2", "aro_cut2"),
    ("ARO/M1", "aro_median1"), ("ARO/M2", "aro_median2"),
    ("FB/C1", "fore_buchholz_cut1"), ("FB/C2", "fore_buchholz_cut2"),
    ("FB/M1", "fore_median1"), ("FB/M2", "fore_median2"),
]


def test_named_equivalence(swiss4):
    for pid in swiss4:
        for descriptor, named in _NAMED_PAIRS:
            assert calculate_descriptor(
                swiss4[pid], swiss4, descriptor, TR) == pytest.approx(
                    f26.calculate(swiss4[pid], swiss4, named, TR))


def test_limit_mapping(swiss4):
    for pid in swiss4:
        assert calculate_descriptor(
            swiss4[pid], swiss4, "KS/L+1", TR) == pytest.approx(
                f26.koya(swiss4[pid], swiss4, TR, "swiss", 0.5, False,
                         0.5))
        assert calculate_descriptor(
            swiss4[pid], swiss4, "KS/L-2", TR) == pytest.approx(
                f26.koya(swiss4[pid], swiss4, TR, "swiss", 0.5, False,
                         -1.0))


def test_forfeit_flag_routing():
    # R2 forfeit_win vs a strong scheduled opponent (adj 3.0):
    # plain §16.4.1 dummy = min(own 2.0, 3.0) = 2.0; /P plays it (3.0).
    players = {
        1: _mk(1, 2000, 2.0, [
            (2, 1900, 1.0, "white", 1, "played"),
            (4, 1900, 1.0, "white", 2, "forfeit_win")]),
        2: _mk(2, 1900, 0.0, [(1, 2000, 0.0, "black", 1, "played")]),
        4: _mk(4, 1900, 3.0, [
            (1, 2000, 0.0, "black", 2, "forfeit_loss"),
            (5, 1900, 1.0, "white", 1, "played"),
            (5, 1900, 1.0, "white", 3, "played"),
            (5, 1900, 1.0, "white", 4, "played")]),
        5: _mk(5, 1900, 0.0, [
            (4, 1900, 0.0, "black", 1, "played"),
            (4, 1900, 0.0, "black", 3, "played"),
            (4, 1900, 0.0, "black", 4, "played")]),
    }
    plain = calculate_descriptor(players[1], players, "BH", 4)
    flagged = calculate_descriptor(players[1], players, "BH/P", 4)
    assert plain == pytest.approx(0.0 + 2.0)
    assert flagged == pytest.approx(
        f26.buchholz(players[1], players, 4, "swiss", 0.5, True))
    assert flagged == pytest.approx(0.0 + 3.0)
    assert plain != flagged


# ------------------------------------------------------------------
# Generic monotonicity (cutting more never increases the sum)
# ------------------------------------------------------------------

@pytest.mark.parametrize("descriptor_tpl", [
    ("BH/C{0}", [1, 2, 3, 4]),
    ("SB/C{0}", [1, 2, 3]),
    ("FB/C{0}", [1, 2, 3]),
])
def test_cut_monotonicity(swiss4, descriptor_tpl):
    # Sum families: cutting more (non-negative) elements never
    # increases the total.
    tpl, ns = descriptor_tpl
    for pid in swiss4:
        values = [calculate_descriptor(swiss4[pid], swiss4,
                                       tpl.format(n), TR) for n in ns]
        assert all(a >= b for a, b in zip(values, values[1:])), (pid, values)


@pytest.mark.parametrize("descriptor_tpl", [
    ("BH/M{0}", [1, 2]),
    ("FB/M{0}", [1, 2]),
])
def test_median_monotonicity(swiss4, descriptor_tpl):
    tpl, ns = descriptor_tpl
    for pid in swiss4:
        values = [calculate_descriptor(swiss4[pid], swiss4,
                                       tpl.format(n), TR) for n in ns]
        assert all(a >= b for a, b in zip(values, values[1:])), (pid, values)


def test_aro_cut_definition(swiss4):
    # ARO/Cn drops the n lowest rated-OTB-opponent ratings, then the
    # half-up mean (no VUR ratings exist, so cuts are plain).
    # P1 opps: 1900/1950/1800/1900/1950 -> C3 drops 1800,1900,1900.
    assert calculate_descriptor(swiss4[1], swiss4, "ARO/C3", TR) == \
        pytest.approx(1950.0)
    # P4 opps: 1950/1900/2000/1950/1900 -> C3 drops 1900,1900,1950.
    assert calculate_descriptor(swiss4[4], swiss4, "ARO/C3", TR) == \
        pytest.approx(1975.0)


def test_ps_c2_round_exclusion(swiss4):
    # PS/C2 excludes cumulative scores after rounds 1 AND 2.
    for pid in swiss4:
        ps = calculate_descriptor(swiss4[pid], swiss4, "PS", TR)
        c1 = calculate_descriptor(swiss4[pid], swiss4, "PS/C1", TR)
        c2 = calculate_descriptor(swiss4[pid], swiss4, "PS/C2", TR)
        assert ps >= c1 >= c2


# ------------------------------------------------------------------
# Ranking: parity + /R reversal + scope errors
# ------------------------------------------------------------------

def test_rank_parity_with_named_engine(swiss4):
    ranked = rank_descriptors(swiss4, ["BH/C1", "SB/C1"], TR)
    engine = f26.rank_standings(
        swiss4, ["buchholz_cut1", "sonneborn_berger_cut1"], TR)
    assert [p.player_id for p in ranked.players] == [
        p.player_id for p in engine.players]
    assert ranked.rules_version == "fide-2026"


def test_reverse_terminal_direction():
    # Equal points so the terminal stage decides.
    players = {
        1: _mk(1, 2000, 2.0, [(2, 1900, 1.0, "white", 1, "played"),
                              (3, 1900, 1.0, "white", 2, "played")]),
        2: _mk(2, 1900, 2.0, [(1, 2000, 0.0, "black", 1, "played"),
                              (4, 1800, 1.0, "white", 2, "played")]),
        3: _mk(3, 1900, 2.0, [(1, 2000, 0.0, "black", 2, "played"),
                              (4, 1800, 1.0, "white", 1, "played")]),
        4: _mk(4, 1800, 2.0, [(2, 1900, 0.0, "black", 2, "played"),
                              (3, 1900, 0.0, "black", 1, "played")]),
    }
    pairing = {1: 4, 2: 3, 3: 2, 4: 1}
    fwd = rank_descriptors(players, ["TPN"], 2, pairing_numbers=pairing)
    rev = rank_descriptors(players, ["TPN/R"], 2, pairing_numbers=pairing)
    assert [p.player_id for p in fwd.players] == [4, 3, 2, 1]
    assert [p.player_id for p in rev.players] == [1, 2, 3, 4]
    rtng = rank_descriptors(players, ["RTNG"], 2)
    rtng_rev = rank_descriptors(players, ["RTNG/R"], 2)
    assert [p.player_id for p in rtng.players][0] == 1  # 2000 first
    assert [p.player_id for p in rtng_rev.players][-1] == 1  # 2000 last


def test_rank_rejects_team_descriptors(swiss4):
    with pytest.raises(UnsupportedCriterionError):
        rank_descriptors(swiss4, ["BH:MP/C1"], TR)


def test_calculate_rejects_stages_and_teams(swiss4):
    with pytest.raises(UnsupportedCriterionError):
        calculate_descriptor(swiss4[1], swiss4, "DE", TR)
    with pytest.raises(UnsupportedCriterionError):
        calculate_descriptor(swiss4[1], swiss4, "TPN", TR)
    with pytest.raises(UnsupportedCriterionError):
        calculate_descriptor(swiss4[1], swiss4, "BH:MP", TR)
    with pytest.raises(UnsupportedCriterionError):
        calculate_descriptor(swiss4[1], swiss4, "EMMSB", TR)


# ------------------------------------------------------------------
# Metamorphic: determinism + non-mutation + permutation
# ------------------------------------------------------------------

def test_descriptor_non_mutation(swiss4):
    before = copy.deepcopy(swiss4)
    for pid in swiss4:
        for descriptor in ("BH/C3", "SB/C2", "ARO/M2", "PS/C2",
                           "KS/L+1", "AOB/F"):
            calculate_descriptor(swiss4[pid], swiss4, descriptor, TR)
    rank_descriptors(swiss4, ["BH/C3", "SB/C2"], TR)
    assert swiss4 == before


def test_descriptor_permutation_invariance(swiss4):
    remapped = {pid + 100: PlayerTiebreakData(
        player_id=pid + 100, rating=p.rating, points=p.points,
        games=[GameRecord(
            opponent_id=(g.opponent_id + 100
                         if g.opponent_id != -1 else -1),
            opponent_rating=g.opponent_rating, score=g.score,
            color=g.color, round_number=g.round_number, kind=g.kind)
            for g in p.games]) for pid, p in swiss4.items()}
    for pid in swiss4:
        for descriptor in ("BH/C3", "BH/M2", "SB/C2", "PS/C2"):
            assert calculate_descriptor(
                swiss4[pid], swiss4, descriptor, TR) == pytest.approx(
                    calculate_descriptor(remapped[pid + 100], remapped,
                                         descriptor, TR))
