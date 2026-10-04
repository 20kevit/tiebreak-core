"""Generate coherent differential fixtures (regen tooling only).

Run from tests/oracle/: ``python3 generate_fixtures.py`` writes
fixtures/*.json (fixed seeds → deterministic output). Every game is
recorded on BOTH sides with opposite colors and complementary
scores; points == recorded sums; every referenced opponent is
present. Element-count rule: every player has >= 5 recorded rounds
(keeps cut/median edge policies out of the comparison). New
fixtures must pass the in-generator coherence audit or generation
aborts. Regenerate oracle values afterwards (see README.md).

Every game is recorded on BOTH sides with opposite colors and
complementary scores; points == recorded sums; every referenced
opponent is present. Element-count rule: every player has >=5
recorded rounds (keeps cut/median edge policies out of the
comparison). Ratings: 1200-2400 for all (plus one unrated case).
Output: fixture JSON files {players, total_rounds, mode}.
"""
import json
import random

OUT = 'fixtures'


def emit(name, players, total_rounds, mode='swiss'):
    import os
    os.makedirs(OUT, exist_ok=True)
    # coherence audit
    ids = set(players)
    for pid, p in players.items():
        s = sum(g['score'] for g in p['games'])
        assert abs(s - p['points']) < 1e-9, (name, pid, s, p['points'])
        assert len(p['games']) >= 5, (name, pid, 'fewer than 5 rounds')
        for g in p['games']:
            if g['kind'] == 'played':
                assert g['opponent'] in ids, (name, pid, g)
                back = [h for h in players[g['opponent']]['games']
                        if h['opponent'] == pid and h['round'] == g['round']
                        and h['kind'] == 'played']
                assert len(back) == 1, (name, pid, g, 'no mutual back-link')
                b = back[0]
                assert b['color'] != g['color'], (name, pid, g, 'color')
                assert abs(b['score'] - (1.0 - g['score'])) < 1e-9 \
                    or (b['score'] == 0.5 and g['score'] == 0.5), \
                    (name, pid, g, 'score')
    with open(f'{OUT}/{name}.json', 'w') as f:
        json.dump({'players': players, 'total_rounds': total_rounds,
                   'mode': mode}, f)
    print(f'wrote {name}: {len(players)} players, {total_rounds} rounds')


def P(pid, rating, games):
    pts = sum(g[1] for g in games)
    return {'rating': rating, 'points': pts,
            'games': [{'opponent': o, 'score': s, 'color': c, 'round': r,
                       'rating': 1500, 'kind': k}
                      for (o, s, c, r, k) in games]}


def fp_event(n, rounds, seed):
    """Fully-played Swiss-style event, mutual records."""
    rng = random.Random(seed)
    ratings = {i + 1: 1200 + 100 * ((i * 37) % 13) for i in range(n)}
    games = {i + 1: [] for i in range(n)}
    for r in range(1, rounds + 1):
        order = list(range(1, n + 1))
        rng.shuffle(order)
        if n % 2:
            order = order[:-1]
        for a, b in zip(order[::2], order[1::2]):
            s = rng.choice([0.0, 0.5, 1.0])
            ca = 'white' if (a + r) % 2 else 'black'
            cb = 'black' if ca == 'white' else 'white'
            games[a].append((b, s, ca, r, 'played'))
            games[b].append((a, 1.0 - s if s != 0.5 else 0.5, cb, r,
                             'played'))
    players = {pid: P(pid, ratings[pid], games[pid]) for pid in games
               if len(games[pid]) == rounds}
    # keep only full-attendance players, renumbered densely
    keep = sorted(players)
    return {i + 1: {'rating': players[pid]['rating'],
                    'points': players[pid]['points'],
                    'games': [{'opponent': keep.index(g['opponent']) + 1,
                               'score': g['score'], 'color': g['color'],
                               'round': g['round'], 'rating': 1500,
                               'kind': 'played'}
                              for g in players[pid]['games']]}
            for i, pid in enumerate(keep)}, rounds


def unplayed_event(n, rounds, seed):
    """Swiss event with byes/forfeits (scheduled opponents known)."""
    rng = random.Random(seed)
    ratings = {i + 1: 1200 + 100 * ((i * 53) % 13) for i in range(n)}
    games = {i + 1: [] for i in range(n)}
    for r in range(1, rounds + 1):
        order = list(range(1, n + 1))
        rng.shuffle(order)
        if n % 2:
            odd = order.pop()
            roll = rng.random()
            if roll < 0.5:
                games[odd].append((-1, 1.0, 'white', r, 'pairing_bye'))
            elif roll < 0.8:
                games[odd].append((-1, 0.5, 'white', r, 'requested_bye'))
            else:
                games[odd].append((-1, 0.0, 'white', r, 'requested_bye'))
        for a, b in zip(order[::2], order[1::2]):
            roll = rng.random()
            ca = 'white' if (a + r) % 2 else 'black'
            cb = 'black' if ca == 'white' else 'white'
            if roll < 0.82:
                s = rng.choice([0.0, 0.5, 1.0])
                games[a].append((b, s, ca, r, 'played'))
                games[b].append((a, 1.0 - s if s != 0.5 else 0.5, cb, r,
                                 'played'))
            elif roll < 0.91:
                games[a].append((b, 1.0, ca, r, 'forfeit_win'))
                games[b].append((a, 0.0, cb, r, 'forfeit_loss'))
            else:
                games[a].append((b, 0.0, ca, r, 'forfeit_loss'))
                games[b].append((a, 1.0, cb, r, 'forfeit_win'))
    players = {}
    for pid in range(1, n + 1):
        if len(games[pid]) == rounds:
            players[pid] = P(pid, ratings[pid], games[pid])
    return players, rounds


if __name__ == '__main__':
    p, r = fp_event(6, 5, 101)
    emit('fp_6x5', p, r)
    p, r = fp_event(10, 7, 202)
    emit('fp_10x7', p, r)
    p, r = fp_event(12, 9, 303)
    emit('fp_12x9', p, r)
    p, r = unplayed_event(8, 7, 404)
    emit('up_8x7', p, r, 'swiss')
    p, r = unplayed_event(10, 7, 505)
    emit('up_10x7b', p, r, 'swiss')
