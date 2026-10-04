// Differential oracle driver (regen tooling only — never run by pytest).
//
// Usage (see README.md):
//   npm install <pinned @echecs/* packages>
//   node driver_echecs.mjs fixtures/ > echecs_NEW.json
//
// Reads every tests/oracle/fixtures/*.json fixture, translates the
// normalized GameRecord model to the echecs CompletedRound model, and
// prints {meta, cases: {name: {fixture, echecks}}} JSON.
// Translation contract (must match test_differential.py assumptions):
//   - played: mutual records, result from White's perspective;
//   - forfeit_win/loss with a scheduled opponent -> forfeit flag;
//     forfeits with unknown pairings are SKIPPED (no oracle basis);
//   - pairing_bye -> {kind: 'pairing'}; requested_bye 1.0/0.5/0.0 ->
//     'full'/'half'/'zero'; player ratings passed through (0 omits).
import { createRequire } from 'module';
import { readdirSync, readFileSync } from 'fs';
import { join } from 'path';
const require = createRequire(process.cwd() + '/');
const BH = require('@echecs/buchholz');
const BHC1 = require('@echecs/buchholz/cut1');
const BHC2 = require('@echecs/buchholz/cut2');
const BHM1 = require('@echecs/buchholz/median1');
const BHM2 = require('@echecs/buchholz/median2');
const BHFORE = require('@echecs/buchholz/fore');
const BHFC1 = require('@echecs/buchholz/fore-cut1');
const BHFC2 = require('@echecs/buchholz/fore-cut2');
const BHFM1 = require('@echecs/buchholz/fore-median1');
const BHFM2 = require('@echecs/buchholz/fore-median2');
const BHAV = require('@echecs/buchholz/average');
const BHAVF = require('@echecs/buchholz/average-fore');
const SB = require('@echecs/sonneborn-berger');
const SBC1 = require('@echecs/sonneborn-berger/cut1');
const SBC2 = require('@echecs/sonneborn-berger/cut2');
const KO = require('@echecs/koya');
const AR = require('@echecs/average-rating');
const ARC1 = require('@echecs/average-rating/cut1');
const ARC2 = require('@echecs/average-rating/cut2');
const ARM1 = require('@echecs/average-rating/median1');
const ARM2 = require('@echecs/average-rating/median2');
const PS = require('@echecs/progressive');
const DE = require('@echecs/direct-encounter');

const FNS = {
  buchholz: BH.tiebreak, buchholz_cut1: BHC1.tiebreak,
  buchholz_cut2: BHC2.tiebreak, median_buchholz: BHM1.tiebreak,
  median_buchholz_2: BHM2.tiebreak, fore_buchholz: BHFORE.tiebreak,
  fore_buchholz_cut1: BHFC1.tiebreak, fore_buchholz_cut2: BHFC2.tiebreak,
  fore_median1: BHFM1.tiebreak, fore_median2: BHFM2.tiebreak,
  aob: BHAV.tiebreak, aob_fb: BHAVF.tiebreak,
  sonneborn_berger: SB.tiebreak, sonneborn_berger_cut1: SBC1.tiebreak,
  sonneborn_berger_cut2: SBC2.tiebreak, koya: KO.tiebreak,
  aro: AR.tiebreak, aro_cut1: ARC1.tiebreak, aro_cut2: ARC2.tiebreak,
  aro_median1: ARM1.tiebreak, aro_median2: ARM2.tiebreak,
  progressive: PS.tiebreak, de_score: DE.directEncounter,
};

function translate(F) {
  const ids = Object.keys(F.players);
  const rounds = [];
  for (let r = 1; r <= F.total_rounds; r++) rounds.push({ games: [], byes: [] });
  const seen = new Set();
  for (const [pid, p] of Object.entries(F.players)) {
    for (const g of p.games) {
      const r = g.round;
      if (r < 1 || r > F.total_rounds) continue;
      const k = g.kind || (g.opponent === -1 ? 'unplayed' : 'played');
      if (k === 'played') {
        const key = [Math.min(+pid, g.opponent), Math.max(+pid, g.opponent), r].join(':');
        if (seen.has(key)) continue;
        seen.add(key);
        const white = g.color === 'white' ? String(pid) : String(g.opponent);
        const black = g.color === 'white' ? String(g.opponent) : String(pid);
        const result = g.score === 1 ? (g.color === 'white' ? 'white' : 'black')
          : g.score === 0 ? (g.color === 'white' ? 'black' : 'white') : 'draw';
        rounds[r - 1].games.push({ white, black, result });
      } else if ((k === 'forfeit_win' || k === 'forfeit_loss') && g.opponent !== -1) {
        const iWon = k === 'forfeit_win';
        const meWhite = g.color === 'white';
        const white = meWhite ? String(pid) : String(g.opponent);
        const black = meWhite ? String(g.opponent) : String(pid);
        const forfeited = (iWon === meWhite) ? 'black' : 'white';
        const result = (iWon === meWhite) ? 'white' : 'black';
        const key = ['f', Math.min(+pid, g.opponent), Math.max(+pid, g.opponent), r].join(':');
        if (seen.has(key)) continue;
        seen.add(key);
        rounds[r - 1].games.push({ white, black, forfeit: forfeited, result });
      } else if (k === 'pairing_bye') {
        rounds[r - 1].byes.push({ kind: 'pairing', player: String(pid) });
      } else if (k === 'requested_bye') {
        const kind = g.score === 1 ? 'full' : g.score === 0.5 ? 'half' : 'zero';
        rounds[r - 1].byes.push({ kind, player: String(pid) });
      }
    }
  }
  const players = ids.map(pid => {
    const p = { id: String(pid), points: F.players[pid].points };
    if (F.players[pid].rating > 0) p.rating = F.players[pid].rating;
    return p;
  });
  return { rounds, players, ids };
}

const dir = process.argv[2] || 'fixtures';
const cases = {};
for (const f of readdirSync(dir).filter(f => f.endsWith('.json')).sort()) {
  const F = JSON.parse(readFileSync(join(dir, f), 'utf8'));
  const { rounds, players, ids } = translate(F);
  const out = {};
  for (const pid of ids) {
    out[pid] = {};
    for (const [name, fn] of Object.entries(FNS)) {
      try {
        const v = fn(String(pid), rounds, players);
        out[pid][name] = (typeof v === 'number' && Number.isFinite(v)) ? v : 'NONNUM:' + String(v);
      } catch (e) { out[pid][name] = 'ERROR:' + e.message; }
    }
  }
  cases[f.replace(/\.json$/, '')] = { fixture: F, echecks: out };
}
console.log(JSON.stringify({ meta: 'see README.md for package pins; regenerate, do not hand-edit', cases }, null, 1));
