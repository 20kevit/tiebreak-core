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

## ETT26 — Encoded Type (of tournament) Table (CORRECTED 2026-10-03)

A prior revision of this document falsely concluded "ETT26 does not
exist". That conclusion is withdrawn: ETT26 exists as **C.02.03
Annex C — Tournament Type Code Table (for TRF_CODE 192)**
(`handbook.fide.com/files/handbook/ETT26.pdf`, Roberto Ricca).
It is NOT a test format; it is the code table for TRF26 field 192,
i.e. the tournament/system classifier. (The earlier search confused
the acronym with unrelated "ETT" test products.)

Content (verified: TEC Apr-2025 `TournamentTypeCodeTable192-TRF26.pdf`
extracted in full, 96 lines; Handbook ETT26 indexed text Precise):

- SWISS FOR INDIVIDUALS: FIDE_DUTCH_* (+_BAKU), FIDE_DUBOV (±BAKU),
  FIDE_BURSTEIN (±BAKU), CUSTOM_SWISS, FIDE_DOUBLESWISS (±BAKU),
  CUSTOM_DOUBLESWISS. Version note: TEC draft uses DUTCH_2017/2025
  with a July-1-2025 cutover; Handbook ETT26 uses DUTCH_2017/2026
  with a Feb-1-2026 cutover — Handbook governs.
- PREDETERMINED PAIRING (INDIVIDUALS): BERGER_ROUNDROBIN_Gn
  (G1 default; G2 = double), FIDE_ROUNDROBIN, FIDE_DOUBLEROUNDROBIN
  (last two rounds reversed + G1), CUSTOM_ROUNDROBIN;
  FIDE_SCHILLER_TxP (default 4x3) / CUSTOM_SCHILLER;
  FIDE_SCHEVENINGEN_Gn (G1 default; G2 = double) / CUSTOM_SCHEVENINGEN;
  CUSTOM_KNOCKOUT. (Berger tables live in Competition Rules
  Appendix 1; SCHILLER/SCHEVENINGEN order/colour rules "not yet
  defined" — flagged, non-blocking: no core inputs depend on them.)
- SWISS FOR TEAMS (TEAM always in code): FIDE_TEAM_TYPEA/B ×
  MP_GP/MP/GP primaries (±BAKU), FIDE_TEAM_MP_GP etc.,
  CUSTOM_TEAM_SWISS.
- PREDETERMINED PAIRING (TEAMS): BERGER_TEAM_ROUNDROBIN_Gn/G1/G2,
  FIDE_TEAM_ROUNDROBIN (+DOUBLE), CUSTOM_TEAM_ROUNDROBIN.
- OTHER: CUSTOM_TEAM_KNOCKOUT.

Tie-break relevance is ONLY the regime mapping (consumer-owned):
Swiss codes → C.07 Article 16; Berger/Schiller/Scheveningen codes →
predetermined-pairing regime (C.07 §15.2, incl. the 2026 carve-out);
KNOCKOUT codes → play-off/§12 context; CUSTOM_* → organiser-defined
(`OTHER_*` descriptors; explicit mapping, never inferred).
Conformance interfaces remain: (a) official worked examples
(corpus), (b) RTG-style seeded generation, (c) PTC-style
differential checks.

## What this means for tiebreak-core now

Deterministic pure functions + exact arithmetic + typed errors +
ruleset pins + TRF-descriptor-compatible ids + corpus-first
development already satisfy the *library* side of 1–4. Approval-side
artifacts (PTC/RTG CLIs, VCL/SDPC/TAPC, fees, registers) belong to a
THP vendor, never to this package (see approval-path doc).
