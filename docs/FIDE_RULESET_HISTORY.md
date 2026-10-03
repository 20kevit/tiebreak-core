# FIDE ruleset history (C.07 chronology)

Confidence tags: `RETRIEVED` = full/extracted primary text read this
mission; `SECONDARY` = Handbook index snippets / FIDE news / third-party
walk-throughs; `UNVERIFIED` = not confirmed. Handbook chapter URLs are
listed but were unreachable from this environment (direct fetch times
out); contents below rest on PDFs + manual + snippets, never on memory.

| Edition | Effective | Approved | Status |
|---|---|---|---|
| pre-2023 (`TieBreakRegulationsPre2023`) | till 31 Aug 2023 (2022 text: applied 1 Jul 2023) | FIDE Council 04/08/2022 | RETRIEVED (2022 draft PDF) / SECONDARY (archive chapter) |
| Sep-2023 (`TieBreakRegulations2023`) | 1 Sep 2023 → 31 Mar 2024 (all rated events only from 1 Apr 2024) | FIDE Council 01/08/2023 | RETRIEVED (official Table of Changes) |
| Apr-2024 (`TieBreakRegulations042024`) | 1 Apr 2024 → 31 Jul 2024 | FIDE Council 14/12/2023 (3rd FC 2023, Annex C.07) | RETRIEVED (decision PDF + FIDE news) |
| Aug-2024 (`TieBreakRegulations082024`) | 1 Aug 2024 → 28 Feb 2026 | FIDE Council 29/07/2024 (CM2-2024/18) | RETRIEVED (full text) |
| Mar-2026 (`TieBreakRegulations032026`) | from 1 Mar 2026 (current) | FIDE Council 02/02/2026 | RETRIEVED (full text via Arbiter Manual 2026); decision instrument number UNVERIFIED |

## pre-2023 — virtual-opponent/self-game regime

Source: `spp.fide.com/wp-content/uploads/20220629-Tie-Breaks-2.pdf`
(RETRIEVED). Scope covered only EVE/GSC events (recommended for rated
events). Unplayed management lived in **Article 14**:

- 14.3.1–14.3.5 five categories (PAB/forfeit-win/full-point bye;
  requested bye followed by available-to-play; forfeit loss followed by
  available-to-play; requested bye NOT followed; forfeit loss NOT
  followed).
- 14.4 opponent-side adjustment (.1–.3 at face value, .4–.5 as draws).
- 14.5 **self-game rule**: own tie-break as if the player played
  *themself* with the awarded result.
- 14.6 low-cut rule: unplayed rounds of cats .2–.5 cut first.
- 14.7 organiser opt-out.
- Rest: Type A/B/C/**D** taxonomy (D = ratings/current scores); DE =
  percentage score (§5.1); Fore Buchholz *"as if … the upcoming round
  ended in draws"*; SB on *"current (or final)"* scores; PTP via
  zero-rating-variation; team-KO condition looser than today.

`tiebreak-core` relevance: none of this regime is implemented, and it
must never leak into `fide-2024` (cf. Tornelo's virtual-opponent
toggle — a workaround for exactly this legacy).

## Sep-2023 — full rewrite ("PLAY-OFF AND TIE-BREAK REGULATIONS")

Source: `doc.fide.com/docs/DOC/2FC2023/PO_and_TB_Regulations_Table_of_Changes.pdf`
(RETRIEVED, 203 lines). Header: applied 1 Sep 2023 for EVE/GSC,
1 Apr 2024 for all rated competitions. Changes:

- **Virtual opponent abolished**; Art 14.5 self-game → new **Art 16.4
  dummy rule** (dummy finishes on the participant's own points).
- New Articles 14 (modifiers) / 15 (unplayed rounds; forfeits in
  pre-determined pairings = regular games) / 16 (Swiss management:
  16.2.1–16.2.5 categories, 16.3 opponent adjustment, 16.4 dummy,
  16.5 cut exception, 16.6 opt-out).
- **DE rewritten** (new Art 6): forfeit exclusion 6.1.1,
  repeated-meeting averaging 6.1.2, Swiss partial-DE + reapplication
  6.2/6.3.
- Type D abolished → Arts 8/9/10; SB strictly **final** scores; PTP
  redefined via expected-score table; new SB-C1; Median order
  clarified; Fore Buchholz → "final round"; team-KO conditioned on
  equal MP **and** GP; SSSC typed BC/BD.
- Governance: scope = all rated competitions; Art 2 ranking
  reframed; Cut-1 column in the Article 5 table.

## Apr-2024 — clarification-only

Source: `doc.fide.com/docs/DOC/3FC2023/FC3_2023_43.pdf` (RETRIEVED)
+ `fide.com/updated-tie-break-regulations-effective-from-april-1-2024-published`
(RETRIEVED): *"no alterations have been made to the tie-break
definitions themselves… refine the explanations."* Deltas: **VUR**
acronym introduced (Art 16.5 intro), dummy clarified to the
participant's **final** score, Art 4.2 gains the *"unless … ties will
not be broken"* tail (SECONDARY attribution).

## Aug-2024 — editorial (basis of ruleset `fide-2024`)

Source: `doc.fide.com/docs/DOC/2FC2024/2024_FC2_18.pdf` (RETRIEVED,
full text) + `2024_FC2_18_TOC.pdf` (RETRIEVED Table of Changes).
Deltas vs Apr-2024 are editorial only:

- Art 2.1 default behaviour when regulations are silent (apply
  2.2.2 + 4.1.1); 2.2.1/2.2.2 numbering; new 4.1.1 text.
- GE → **REP** rename ("Rounds one Elected to Play").
- Art 13.3 partial-DE wording ("no ties were broken per this rule").
- Art 14.1 Cut-1 redefined from cutting *opponents* to cutting
  *values* (BH-C1 lowest points; SB-C1 lowest product with
  worst-result tiebreak; ESB primary-score reference removed).
- Art 14.5 Koya language; Art 16.1.2 "available-to-play round"
  deleted in favour of "non-VUR"; 16.2.3/16.2.5 reworded.

## Mar-2026 — current (basis of specified `fide-2026`)

Source: full text via FIDE Arbiters' Manual 2026 (RETRIEVED);
announcement `fide.com/…-effective-march-1-2026` (RETRIEVED).
Complete verified delta vs Aug-2024: `docs/FIDE_2026_DIFF.md`
(D1–D15). In brief: 3 new criteria (STD §7.7, TPN §7.8, RTNG §10.6);
Buchholz round-robin ban; AOB Fore-BH note; multi-rating rule;
EDE+knockout chain names; §15.2 forfeit carve-out; **§16.4 dummy
caps** (the one semantic change affecting Swiss BH/SB); official
worked-examples annex.

Residual uncertainty: the 02/02/2026 approving instrument has no
public number/URL in indexed sources (UNVERIFIED); fine
Sep-2023→Apr-2024 article blame is SECONDARY (FIDE says definitions
unchanged, so nothing hangs on it).
