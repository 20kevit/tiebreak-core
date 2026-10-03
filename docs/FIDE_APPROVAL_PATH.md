# FIDE approval path (conformant vs approved)

## The three levels (never collapse)

1. **FIDE-conformant calculations** — what this library targets:
   every implemented value traceable to a C.07 article + official
   example + corpus case, under explicit frozen rulesets. Correct
   language: "FIDE-conformant", "FIDE-aligned", "FIDE-ready",
   "candidate calculation core". Achieved per-criterion (matrix),
   never claimed wholesale beyond implemented rows.
2. **Tournament-management-system compliance** — a THP embedding the
   core must additionally: cover all MTB26 codes, speak TRF26
   (202/212 incl. `OTHER_*`, 192/013/240/320/801/802), ship PTC+RTG,
   support ITDX, track Acceptance Cycles, and pass 50k differential
   verification (≤10 analysed discrepancies). This is vendor work.
3. **FIDE approval/certification** — VCL → SDPC → TAPC (≥3 testers,
   exact version, Council grant) → optional FEAP endorsement
   (commercial agreement). Granted to a THP version, never to a
   library. Gacrux precedent: reference engines are explicitly "not
   FIDE approved".

## What would be required (ordered)

Research → Specification → Architecture → Implementation →
Official corpus → Differential validation → Performance →
FIDE conformance testing → Release → (vendor THP) TAPC path.
No step may be skipped; no "FIDE-approved" wording may appear before
the Council grant — which is out of this repository's scope by
design. The roadmap's Phase F26-1 completes level 1 for the
individual-Swiss domain; levels 2–3 belong to a future THP vendor
using this core with file-transparent I/O (cf. external-engine
exemption, TEC Manual §3.9.4).

## Timing caveat (verified, Samarkand Congress 2026 paper)

Tie-break/standings TAPC testing starts **for the first time in the
future** (TEC: "we will be testing tie-breaks and standings for the
first time in the future"); the THP Verification Checklist is not yet
final ("Next Acceptance Cycle authorised, subject to the final THP
VCL"). Consequence: no vendor holds a tie-break TAPC under the 2026
protocol today, and no fixed expected-output suite exists — approval
is and will remain differential (RTG-seeded, PTC cross-checked), not
golden. The Gacrux reference (MIT, GitHub, 120k+ generated
tournaments; pairing + tie-break + generator components embeddable in
a THP; JSON + TRF-26) is the practical oracle in the meantime — and is
itself explicitly "not FIDE approved".
