"""
Tie-break registry metadata (identifiers only).

The calculation path (calculators.py) depends ONLY on the stable string
identifiers below. Human-readable presentation strings live in
``tiebreak_core.display`` and must never affect calculation or ranking.

Phase 0 hardening (additive, legacy-compatible):
  - ``frozen_registry()`` exposes an immutable snapshot view so callers
    cannot mutate the calculation registry accidentally.
  - ``register_criterion()`` is the single controlled entry point for
    custom criteria. It REFUSES to overwrite built-in ids (raises
    ``RegistryError``) instead of silently replacing them.
  - The legacy mutable ``TIEBREAK_REGISTRY`` dict in ``calculators.py``
    is left untouched for backward compatibility.
"""
from types import MappingProxyType
from typing import Callable, Dict, List, Mapping, Tuple

from tiebreak_core.errors import RegistryError

TIEBREAK_IDS: Tuple[str, ...] = (
    "buchholz",
    "buchholz_cut1",
    "buchholz_cut2",
    "median_buchholz",
    "median_buchholz_2",
    "sonneborn_berger",
    "progressive",
    "wins",
    "wins_black",
    "games_black",
    "aro",
    "koya",
    "buchholz_sum",
    "arpo",
    "direct_encounter",
)

# FIDE C.07 cross-reference for roadmap work (informational only in v0.1.0).
TIEBREAK_FIDE_REF: Dict[str, str] = {
    "buchholz": "C.07 §8.1 BH",
    "buchholz_cut1": "C.07 §14.1a BH-C1",
    "buchholz_cut2": "C.07 §14.2 BH-C2",
    "median_buchholz": "C.07 §14.3 BH-M1",
    "median_buchholz_2": "C.07 §14 BH-M2",
    "sonneborn_berger": "C.07 §9.1 SB",
    "progressive": "C.07 §7.5 PS",
    "wins": "C.07 §7.1 WIN/WON",
    "wins_black": "C.07 §7.4 BWG",
    "games_black": "C.07 §7.3 BPG",
    "aro": "C.07 §10.1 ARO",
    "koya": "C.07 §9.2 KS (RR-only per FIDE; legacy applies to Swiss)",
    "buchholz_sum": "non-FIDE extension (Buchholz of Buchholz)",
    "arpo": "C.07 §10.4 APRO (legacy uses simplified dp table)",
    "sonneborn_berger_cut1": "C.07 §14.1.1.d SB-C1 (fide-2024)",
    "progressive_cut1": "C.07 §14.1.1.c PS-C1 (fide-2024)",
    "aro_cut1": "C.07 §14.1.1.b ARO-C1 (fide-2024)",
    "aob": "C.07 §8.2 AOB (fide-2024)",
    "fore_buchholz": "C.07 §8.3 FB (fide-2024)",
    "won": "C.07 §7.2 WON (fide-2024; legacy 'wins' counts all 1.0)",
    "rounds_elected": "C.07 §7.6 REP (fide-2024)",
    "tpr": "C.07 §10.2 TPR (fide-2024)",
    "ptp": "C.07 §10.3 PTP (fide-2024)",
    "apro": "C.07 §10.4 APRO (fide-2024)",
    "appo": "C.07 §10.5 APPO (fide-2024)",
    "direct_encounter": "C.07 §6 DE (legacy standings-level value is a 0.0 stub)",
    "tpn": "C.07 §7.8 TPN (fide-2026 terminal ranking stage, ascending)",
    "rtng": "C.07 §10.6 RTNG (fide-2026 terminal ranking stage, descending)",
    "std": "C.07 §7.7 STD (fide-2026; needs scheduled-opp round scores)",
    "sonneborn_berger_cut2": "C.07 §14.2 SB-C2 (fide-2026)",
    "aro_cut2": "C.07 §14.2 ARO-C2 (fide-2026)",
    "fore_buchholz_cut1": "C.07 §8.3+§14.1.1 FB-C1 (fide-2026)",
    "fore_buchholz_cut2": "C.07 §8.3+§14.2 FB-C2 (fide-2026)",
    "aob_fb": "C.07 §8.2 AOB over Fore BH (fide-2026)",
    "fore_median1": "C.07 §8.3+§14.3 FB-M1 (fide-2026)",
    "fore_median2": "C.07 §8.3+§14.4 FB-M2 (fide-2026)",
    "aro_median1": "C.07 §10.1+§14.3 ARO-M1 (fide-2026)",
    "aro_median2": "C.07 §10.1+§14.4 ARO-M2 (fide-2026)",
}

DEFAULT_CRITERIA: List[str] = [
    "buchholz_cut1",
    "buchholz",
    "sonneborn_berger",
    "progressive",
]


def frozen_registry() -> Mapping[str, Callable]:
    """Return an immutable snapshot of the calculation registry.

    Mutating the result raises ``TypeError``. The snapshot reflects the
    registry (built-ins + any custom criteria registered so far) at call
    time; later registrations do not retroactively appear in it.
    """
    from tiebreak_core.calculators import TIEBREAK_REGISTRY

    return MappingProxyType(dict(TIEBREAK_REGISTRY))


def is_known(criterion: str) -> bool:
    """Return True iff ``criterion`` resolves on the calculation path."""
    from tiebreak_core.calculators import TIEBREAK_REGISTRY

    return criterion in TIEBREAK_IDS or criterion in TIEBREAK_REGISTRY


def register_criterion(criterion: str, func: Callable) -> None:
    """Register a custom criterion under controlled conditions.

    - Built-in ids (``TIEBREAK_IDS``) can NEVER be overwritten; attempting
      to do so raises ``RegistryError``.
    - Re-registering your OWN custom id replaces it (explicit, not silent
      for built-ins — the dangerous case is refused outright).
    - ``func`` must be callable with signature
      ``(player, all_players) -> float``.

    No dynamic package scanning or global auto-discovery is performed;
    registration is always an explicit call.
    """
    from tiebreak_core.calculators import TIEBREAK_REGISTRY

    if criterion in TIEBREAK_IDS:
        raise RegistryError(
            f"refusing to overwrite built-in criterion {criterion!r}"
        )
    if not callable(func):
        raise RegistryError(
            f"criterion func for {criterion!r} must be callable"
        )
    TIEBREAK_REGISTRY[criterion] = func


def unregister_criterion(criterion: str) -> None:
    """Remove a previously registered CUSTOM criterion.

    Built-in ids cannot be removed (raises ``RegistryError``); unknown ids
    are a no-op. Primarily for test isolation.
    """
    from tiebreak_core.calculators import TIEBREAK_REGISTRY

    if criterion in TIEBREAK_IDS:
        raise RegistryError(
            f"refusing to remove built-in criterion {criterion!r}"
        )
    TIEBREAK_REGISTRY.pop(criterion, None)
