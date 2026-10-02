# Integration: pairing-core consumes tiebreak-core (narrow contract)

Verified against pairing-core 0.1.0 API
(`PlayerData`, `PairingRequest`/`EngineRequest`, `RoundResult`,
`PairingEngine.pair()`).

## Rule

No dependency between the libraries in either direction. If a future
pairing system needs tie-break-derived ordering (e.g. Burstein's
Buchholz-ordered groups), the CALLER (chess-manager, or pairing-core's
own caller) passes precomputed scalars/vectors across the boundary:

```python
from tiebreak_core import calculate_all_strict

# Caller side: compute once, pass plain data.
buchholz = {
    pid: calculate_all_strict(p, players, ["buchholz"], total_rounds,
                              ruleset="legacy-0.1.0")["buchholz"]
    for pid, p in players.items()
}
# ... hand `buchholz: Mapping[int, float]` to whatever pairing routine
# needs ordering input. pairing-core never imports tiebreak-core.
```

## Why scalars, not a dependency

- Burstein-style ordering needs NUMBERS (a sort key), not a calculation
  engine. A `Mapping[int, float]` plus the producing `ruleset` id is the
  complete contract.
- Version/metadata travels as data: record which tiebreak-core ruleset
  produced the vector alongside it; pairing behavior that depends on the
  ordering semantics is then reproducible without coupling releases.
- Errors travel as data too: the caller validates with the strict API
  before passing numbers in; pairing-core validates its own inputs.

## What tiebreak-core guarantees for this use

- Deterministic values per (inputs, ruleset).
- Stable criterion ids (see `TIEBREAK_IDS`); new criteria are additive.
- Frozen legacy outputs; FIDE-correct numbers only under explicit new
  rulesets (`fide-2026` when implemented).
