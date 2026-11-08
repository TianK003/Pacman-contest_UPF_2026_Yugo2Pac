"""Check that eval/rl/game_pool.py reproduces eval/evaluate.py results (same scores on recorded games).

usage: venv_rl\\Scripts\\python.exe eval\\rl\\check_pool.py RUN AGENT [N]
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_pool import GamePool, league_team, REPO  # noqa: E402


def main():
    run, agent = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    with open(os.path.join(REPO, 'eval', 'results', run + '.jsonl')) as fh:
        recs = [json.loads(l) for l in fh]
    sel = [r for r in recs if agent in (r['red'], r['blue']) and r.get('red_score') is not None][:n]
    jobs = []
    for k, r in enumerate(sel):
        rp, ro = league_team(r['red'])
        bp, bo = league_team(r['blue'])
        jobs.append((rp, ro, bp, bo, r['seed'], (k,)))
    pool = GamePool(workers=3)
    res = sorted(pool.run(jobs), key=lambda x: x['tag'][0])
    pool.close()
    same = 0
    for r, x in zip(sel, res):
        ok = r['red_score'] == x['score']
        same += ok
        print(r['red'], r['blue'], r['seed'], 'evaluate.py', r['red_score'], 'game_pool', x['score'],
              'OK' if ok else 'DIFF', x['error'] or '')
    print('identical %d of %d' % (same, len(sel)))


if __name__ == '__main__':
    main()
