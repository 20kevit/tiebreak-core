# FIDE TEC implementation requirements (what FIDE expects from software)

Primary source: FIDE Technical Commission Policies and Procedures
Manual v1.24 (07 Mar 2026), full-text retrieved (499-line extraction;
hash in registry) + TEC Congress Samarkand-2026 paper + C.02.01
General Regulations (effective 1 Mar 2026) snippets. Handbook prevails
on any discrepancy (TEC Manual §1.1.2).

## What FIDE expects from tie-break software (in a THP)

1. **Implement all MTB26 codes** (`FIDE_MTB26_CATALOG.md`) — the code
   table ("any reasonable value" for generic Cn/Mn/Lx/Kx) is the
   mandatory set for an endorsed program.
2. **Embed a free CLI checker (PTC)**: `program.exe -check file.fid`
   reads TRF26 (must) and TRF16/TRF06 (should, within format limits);
   rebuilds every round, re-pairs with the embedded engine, checks
   standings **per the listed tie-breaks**, and reports
   pairing/standing inconsistencies.
3. **Provide a free CLI generator (RTG)**: widely-parametrised
   (players/teams/rounds/unplayed/acceleration/tie-breaks) simulated
   tournaments as TRF26; pairing rules strictly followed; standings
   correct; results plausibly rating-distributed.
4. **Pass large-scale differential verification**: external RTG →
   50,000 tournaments → candidate PTC; ≤10 discrepancies each analysed;
   >10 → revocation procedure. Discrepancy classes: (a) input-file
   error → RTG provider; (b) candidate error → fix + revocation
   rules; (c) **interpretation divergence → TEC issues an official
   clarification** folded into the next rules revision. (This is why
   the uncertainty register matters: today's ambiguities are
   tomorrow's clarifications.)
5. **Acceptance ladder**: VCL (checklist) → SDPC (self-declaration,
   version-pinned) → TAPC (technical acceptance, min. 3 testers,
   exact-version grant, Council-approved) → FEAP/endorsement
   (separate commercial agreement). Rule changes and major upgrades
   auto-revoke; credible complaints / mishandled defects revoke.
   Acceptance Cycles give vendors implementation windows; VCL items
   post-dating an application don't apply to it.
6. **External-engine exemption**: a THP using an already-accepted
   external pairing+tie-break engine may be exempted — but TEC must
   see the engine's inputs and preferably outputs. (Directly relevant
   to embedding a library like tiebreak-core: file-level transparency
   required.)
7. **Gacrux is reference, not approval**: "Gacrux is an engine, not a
   THP, and is not itself FIDE approved" — it helps demonstrate
   compliance; regulations stay authoritative. CLI tools cover
   pairing, tie-break, ranking checks, test generation; TRF-26 native.

## ETT26 boundary (negative result, recorded)

No FIDE "ETT26" test-tournament format exists in the Manual, the
Congress paper, TEC downloads, or indexed sources (searched
2026-10-03; hits are unrelated ETTs). FIDE test material =
RTG-generated TRFs + PTC cross-checks + published worked examples.
`tiebreak-core` must therefore **consume/generate nothing called
ETT**; conformance interfaces are: (a) official worked examples
(corpus), (b) RTG-style seeded generation (recommended property
harness), (c) PTC-style differential checks (gacrux/echecsjs oracles).
If FIDE ever publishes an ETT, this section gets revised — until
then the boundary is explicit absence.

## What this means for tiebreak-core now

Deterministic pure functions + exact arithmetic + typed errors +
ruleset pins + TRF-descriptor-compatible ids + corpus-first
development already satisfy the *library* side of 1–4. Approval-side
artifacts (PTC/RTG CLIs, VCL/SDPC/TAPC, fees, registers) belong to a
THP vendor, never to this package (see approval-path doc).
