"""CMA-ES (evolution strategy, Hansen 2016) tuning of a lab team's string options against an
opponent pool, with game points as the fitness (local tooling, run with venv_rl/).

- Search space: [0, 1]^d, mapped to each parameter's range (int params rounded).
- Common random numbers: every candidate of a generation plays the same (opponent, seed, colour)
  games; the default configuration (x0) is re-evaluated on them too, so each generation reports a
  paired "candidate - default" difference.
- Fresh tuning seeds every generation (no fixed training maps -> less overfitting to maps).
- The final answer is CMA's mean vector (less winner's-curse than the best sample), checked later
  with eval/evaluate.py on unused seeds.

usage (repo root):
  venv_rl\\Scripts\\python.exe eval\\rl\\cmaes_tune.py --name es1 --team lab6_off --spec SPEC.json
     --opponents greedy_v3 choke exploit_v2 rusher camper feature --seeds-per-gen 5 --gens 20
     --popsize 10 --workers 10 --seed-offset 400
SPEC.json: [{"name": "return_at", "lo": 3, "hi": 15, "type": "int", "x0": 8}, ...]
Outputs eval/rl/runs/<name>.jsonl (one line per generation) and <name>_best.json.
"""
import argparse
import json
import os
import sys
import time

import cma
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_pool import GamePool, league_team, our_points, REPO  # noqa: E402

RUNS = os.path.join(REPO, 'eval', 'rl', 'runs')


def load_seeds(offset, n):
    with open(os.path.join(REPO, 'eval', 'seeds', 'tuning.txt')) as fh:
        seeds = [int(l.split()[0]) for l in fh if l.strip() and not l.startswith('#')]
    out = []
    k = offset
    while len(out) < n:
        out.append(seeds[k % len(seeds)])
        k += 1
    return out


def decode(spec, z):
    opts = {}
    for p, v in zip(spec, z):
        v = min(1.0, max(0.0, float(v)))
        x = p['lo'] + v * (p['hi'] - p['lo'])
        if p.get('type') == 'int':
            x = int(round(x))
            opts[p['name']] = str(x)
        else:
            opts[p['name']] = '%.4g' % x
    return opts


def encode(spec):
    return [(p['x0'] - p['lo']) / float(p['hi'] - p['lo']) for p in spec]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', required=True)
    ap.add_argument('--team', required=True, help='league entry whose path + opts are the base')
    ap.add_argument('--fixed', default='', help='extra fixed opts k=v,k=v added to the base')
    ap.add_argument('--spec', required=True)
    ap.add_argument('--opponents', nargs='+', required=True)
    ap.add_argument('--seeds-per-gen', type=int, default=5)
    ap.add_argument('--seed-offset', type=int, default=400)
    ap.add_argument('--gens', type=int, default=20)
    ap.add_argument('--popsize', type=int, default=10)
    ap.add_argument('--sigma', type=float, default=0.25)
    ap.add_argument('--workers', type=int, default=10)
    ap.add_argument('--deadline', default='', help='HH:MM local time to stop after the current generation')
    args = ap.parse_args()

    with open(args.spec) as fh:
        spec = json.load(fh)
    base_path, base_opts = league_team(args.team)
    if args.fixed:
        base_opts.update(dict(kv.split('=', 1) for kv in args.fixed.split(',')))
    opps = [(n,) + league_team(n) for n in args.opponents]
    os.makedirs(RUNS, exist_ok=True)
    log_path = os.path.join(RUNS, args.name + '.jsonl')
    x0 = encode(spec)
    es = cma.CMAEvolutionStrategy(x0, args.sigma, {'popsize': args.popsize, 'bounds': [0, 1],
                                                    'seed': 20261108, 'verbose': -9})
    pool = GamePool(workers=args.workers)
    default_opts = dict(base_opts)
    default_opts.update(decode(spec, x0))
    seed_cursor = args.seed_offset
    for gen in range(args.gens):
        if args.deadline:
            hh, mm = [int(t) for t in args.deadline.split(':')]
            now = time.localtime()
            if (now.tm_hour, now.tm_min) >= (hh, mm) and now.tm_hour < 12:
                print('deadline reached')
                break
        t0 = time.time()
        zs = es.ask()
        seeds = load_seeds(seed_cursor, args.seeds_per_gen)
        seed_cursor += args.seeds_per_gen
        cands = [dict(base_opts, **decode(spec, z)) for z in zs]
        mean_opts = dict(base_opts, **decode(spec, es.mean))
        configs = cands + [default_opts, mean_opts]
        jobs = []
        for ci, opts in enumerate(configs):
            for name, path, oopts in opps:
                for s in seeds:
                    jobs.append((base_path, opts, path, oopts, s, (ci, name, s, 'red')))
                    jobs.append((path, oopts, base_path, opts, s, (ci, name, s, 'blue')))
        results = pool.run(jobs)
        pts = [[] for _ in configs]
        bad = 0
        for r in results:
            p = our_points(r)
            if p is None:
                bad += 1
                continue
            if r['crashed'] or r['timeout']:
                bad += 1
            pts[r['tag'][0]].append(p)
        fit = [float(np.mean(p)) if p else 0.0 for p in pts]
        es.tell(zs, [-f for f in fit[:len(zs)]])
        rec = {'gen': gen, 'seeds': seeds, 'fitness': fit[:len(zs)], 'default': fit[-2],
               'mean_fit': fit[-1], 'mean_opts': decode(spec, es.mean),
               'best_opts': decode(spec, zs[int(np.argmax(fit[:len(zs)]))]),
               'sigma': float(es.sigma), 'bad': bad, 'games': len(results), 'secs': time.time() - t0}
        with open(log_path, 'a') as fh:
            fh.write(json.dumps(rec) + '\n')
        print('gen %d  best %.3f  pop-mean %.3f  default %.3f  mean-vec %.3f  sigma %.3f  bad %d  %.0fs  %s' % (
            gen, max(fit[:len(zs)]), float(np.mean(fit[:len(zs)])), fit[-2], fit[-1], es.sigma, bad,
            time.time() - t0, rec['mean_opts']), flush=True)
        with open(os.path.join(RUNS, args.name + '_best.json'), 'w') as fh:
            json.dump({'mean_opts': decode(spec, es.mean), 'gen': gen, 'base': args.team,
                       'fixed': args.fixed}, fh, indent=1)
    pool.close()


if __name__ == '__main__':
    main()
