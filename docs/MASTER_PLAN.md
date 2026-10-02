# Master plan — path from extraction to a professional v1.x library

## Baseline (this mission's starting point)

Behavior-preserving extraction (v0.1.x): 14 verbatim calculators under
frozen `legacy-0.1.0`, explicit ranking comparator, strict additive API,
golden + live-equivalence tests, thin chess-manager adapter. Proven:
40 tests, deterministic, stdlib-only.

## Completed in this mission

- Stage B: `main` established (publication blocked only on credentials).
- Stage C: inspectable ruleset model (`RulesetInfo`), VERSIONING policy,
  CHANGELOG, 5 ADRs, `py.typed`, release 0.2.0.
- Stage D: conformance corpus framework + VERIFIED definition cases +
  PENDING `fide-2026` shells; FIDE source research (see FIDE_SOURCES).
- Stage E: Median Buchholz-2 (verified definition) as proof that the
  additive-criterion pipeline works end to end.
- Stage G: pairing-core narrow-contract + chess-manager adapter docs.
- Stage H: consolidated ARCHITECTURE, benchmarks, packaging verification.

## Current gaps (honest list)

- `fide-2026` calculations: reserved, not implemented (needs full
  Article 16 text + taxonomy first).
- Direct Encounter: standings-level stub under legacy.
- Rating-based family incomplete (ARPO simplified; no TPR/PTP/APPO/RTNG).
- Cut variants (SB-C1/PS-C1/ARO-C1), AOB, ForeBH: pending.
- No serialization format (none needed yet — do not invent one).
- GitHub publication pending credentials (sole external blocker).

## Capability matrix (target)

| System | Now | Target phase |
|---|---|---|
| BH / C1 / C2 / M1 | legacy-0.1.0 ✓ | Ph.2 Art.16 variants |
| M2 | ✓ (additive) | done |
| SB / PS / Wins / B-family | legacy ✓ | Ph.2 cut variants |
| DE | stub | Ph.3 |
| Koya | legacy (Swiss-applied) | Ph.2 RR gate |
| ARO / ARPO | legacy (simplified dp) | Ph.4 full tables |
| Art.16 taxonomy | absent | Ph.1 |
| TPR/PTP/APPO/RTNG/AOB/FB | absent | Ph.4 or deferred w/ rationale |

## Release strategy

0.2.0 (foundation) → 0.3.0 (Median-2 + corpus) → 0.x per roadmap phase
→ 1.0 when: `fide-2026` engine + DE + corpus green + consumer adoption.
MAJOR bump only for breaking contract changes (none planned; legacy is
frozen by design).

## Conformance strategy

Corpus-first: every new behavior needs a VERIFIED case (official source
+ independent hand computation) before implementation; PENDING shells
track specified-but-unbuilt behavior. Oracles (@echecs MIT vectors,
BBP/JaVaFo subprocess) cross-check only.

## Integration strategy

chess-manager adopts per-tournament ruleset selection; pairing-core
interacts via scalar/vector data only. No shared tournament-core ever
(revisit requires owner decision + concrete duplicated need).
